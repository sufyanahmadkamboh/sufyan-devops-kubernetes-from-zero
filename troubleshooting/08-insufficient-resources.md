# 08 · Insufficient resources

> Uses the [Minikube cluster](../minikube/README.md) (still running at the end of that lesson). Time: 15 minutes.

Resources run out at two different moments: when you **create a cluster** on a machine that is too small, and when
the cluster is up but a Pod asks for more than any node can give. Both are covered here.

## Part A · A cluster on a machine that is too small

### Problem

A colleague's laptop is low on memory, so they start a cluster with as little memory as possible:

<!-- test: fail; timeout=300; contains=memory; output=tail:6 -->
```bash
minikube start -p tiny --driver=docker --memory=1000mb
```

```text
* [tiny] minikube v1.39.0 on Ubuntu 24.04
  - MINIKUBE_IN_STYLE=false
* Using the docker driver based on user configuration

X Exiting due to RSRC_INSUFFICIENT_REQ_MEMORY: Requested memory allocation 1000MiB is less than the usable minimum of 1800MB
```

### Symptoms, investigation, root cause

The start is refused before anything is created. The message says why: the memory requested is below the minimum
Minikube allows (about 1.8 GB). Kubernetes itself (API server, etcd, controller manager, scheduler, kubelet, CoreDNS)
needs that much before running a single application.

Same rule for kubeadm, which checks it in its preflight: at least **2 CPUs** and **1700 MB** on a control plane
(`[ERROR NumCPU]` / `[ERROR Mem]`).

### Fix and verification

Give the cluster enough (`--memory=2200mb` or more). Make sure the half-created profile is gone:

<!-- test: timeout=120 -->
```bash
minikube delete -p tiny
```

<!-- test: absent=tiny; output -->
```bash
minikube profile list
```

```text
┌──────────┬────────┬────────────┬──────────────┬─────────┬────────┬───────┬────────────────┬────────────────────┐
│ PROFILE  │ DRIVER │  RUNTIME   │      IP      │ VERSION │ STATUS │ NODES │ ACTIVE PROFILE │ ACTIVE KUBECONTEXT │
├──────────┼────────┼────────────┼──────────────┼─────────┼────────┼───────┼────────────────┼────────────────────┤
│ minikube │ docker │ containerd │ 192.168.49.2 │ v1.37.0 │ OK     │ 1     │ *              │ *                  │
└──────────┴────────┴────────────┴──────────────┴─────────┴────────┴───────┴────────────────┴────────────────────┘
```

## Part B · A Pod that does not fit

### Problem

A team deploys a small web application. In the manifest, someone typed the CPU request as `"300"` instead of `300m`.
In Kubernetes, `300m` means 300 millicores (0.3 of a CPU); `300` means **three hundred CPUs**.

<!-- test: contains=deployment.apps/hungry created -->
```bash
cat <<'EOF' | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hungry
spec:
  replicas: 1
  selector:
    matchLabels: {app: hungry}
  template:
    metadata:
      labels: {app: hungry}
    spec:
      containers:
        - name: nginx
          image: nginx:1.30-alpine
          resources:
            requests:
              cpu: "300"        # meant: 300m
              memory: 128Mi
EOF
```

### Symptoms

<!-- test: retry=30; contains=Pending; output -->
```bash
kubectl get pods -l app=hungry
```

```text
NAME                     READY   STATUS    RESTARTS   AGE
hungry-84d6875cb-5mjwf   0/1     Pending   0          0s
```

`Pending` is not an error state of the application: it means "not placed on a node yet". The container was never even
started, so there are no logs to read.

### Initial investigation

Who decides where a Pod runs? The **scheduler**. Its decisions are recorded as events on the Pod.

### Commands

<!-- test: retry=15; contains=Insufficient cpu; output -->
```bash
kubectl describe pod -l app=hungry | sed -n '/^Events:/,$p'
```

```text
Events:
  Type     Reason            Age   From               Message
  ----     ------            ----  ----               -------
  Warning  FailedScheduling  0s    default-scheduler  0/1 nodes are available: 1 Insufficient cpu. preemption: 0/1 nodes are available: 1 Preemption is not helpful for scheduling.
```

What does the node have, and what is already reserved?

<!-- test: contains=Allocatable; contains=cpu; output -->
```bash
kubectl get node minikube -o jsonpath='Allocatable: cpu={.status.allocatable.cpu} memory={.status.allocatable.memory}{"\n"}'
kubectl describe node minikube | sed -n '/Allocated resources:/,/Events:/p'
```

```text
Allocatable: cpu=4 memory=16372440Ki
Allocated resources:
  (Total limits may be over 100 percent, i.e., overcommitted.)
  Resource           Requests    Limits
  --------           --------    ------
  cpu                950m (23%)  100m (2%)
  memory             420Mi (2%)  220Mi (1%)
  ephemeral-storage  0 (0%)      0 (0%)
  hugepages-1Gi      0 (0%)      0 (0%)
  hugepages-2Mi      0 (0%)      0 (0%)
Events:
```

And what does the Pod ask for?

<!-- test: contains=300; output -->
```bash
kubectl get deployment hungry -o jsonpath='{.spec.template.spec.containers[0].resources.requests}{"\n"}'
```

```text
{"cpu":"300","memory":"128Mi"}
```

### Output interpretation

- The `FailedScheduling` event: `0/1 nodes are available: 1 Insufficient cpu`. The scheduler looked at every node and
  none had 300 CPUs free.
- **Requests** are what the scheduler counts: a node fits a Pod when (allocatable − sum of requests already placed) ≥
  the Pod's requests. Actual usage (`kubectl top`) does not matter for scheduling.
- The system Pods already reserve part of the node's CPU (`Allocated resources`).
- With the Docker driver, the Minikube node reports the **host's** CPUs as allocatable (in the CI run of this lab: 4,
  although the cluster was started with `--cpus=2`). A request of 3 CPUs would still have fitted there; 300 never does.

### Root cause

A unit typo: the CPU request is `300` (CPUs) instead of `300m` (millicores), more than any node can offer.

### Fix

Correct the request:

<!-- test: contains=resource requirements updated -->
```bash
kubectl set resources deployment hungry --requests=cpu=300m,memory=128Mi
```

In real work, fix the manifest in Git and apply it again; `set resources` is the quick equivalent for this lab.

### Verification

<!-- test: retry=60; contains=successfully rolled out; output -->
```bash
kubectl rollout status deployment hungry --timeout=10s
kubectl get pods -l app=hungry -o wide
```

```text
Waiting for deployment "hungry" rollout to finish: 1 old replicas are pending termination...
Waiting for deployment "hungry" rollout to finish: 1 old replicas are pending termination...
Waiting for deployment "hungry" rollout to finish: 1 old replicas are pending termination...
deployment "hungry" successfully rolled out
NAME                      READY   STATUS    RESTARTS   AGE   IP           NODE       NOMINATED NODE   READINESS GATES
hungry-68c5c87485-z8fl7   1/1     Running   0          0s    10.244.0.6   minikube   <none>           <none>
```

<!-- test: contains=deleted -->
```bash
kubectl delete deployment hungry
```

## Lesson learned

- A cluster needs resources before any workload: 2 CPUs and about 2 GB for a control plane is the floor.
- `Pending` → `kubectl describe pod` → read the `Events`. `Insufficient cpu` / `Insufficient memory` means the requests
  don't fit; other messages point at taints (`untolerated taint`), node selectors or volumes.
- Scheduling uses **requests**, not real usage. Set requests close to real needs, and watch the units: `300m` is
  0.3 CPU, `300` is three hundred CPUs; the cluster autoscaler (on EKS) adds
  nodes when Pods are Pending for lack of resources.
- On a node that really runs out of memory, the kubelet reports `MemoryPressure` and evicts Pods; the Linux OOM killer
  ends containers that go above their memory **limit** (`OOMKilled` in `kubectl describe pod`).

Back to the [troubleshooting index](README.md) · Clean up the Minikube cluster: [minikube/cleanup.md](../minikube/cleanup.md)
