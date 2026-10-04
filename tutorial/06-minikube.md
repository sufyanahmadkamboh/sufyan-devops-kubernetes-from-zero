# 06 · Minikube

> Goal: run Kubernetes on your own computer in one command, work with several clusters at once, and diagnose a Pod
> that does not fit. Time: about 75 minutes. Level 6 of the [roadmap](../README.md#4-the-roadmap).

## Before you start

- Docker answers (`docker version` shows a Server section).
- At least 4 GB of free memory. If the kubeadm VMs from chapters 02–05 are still running and your computer has less
  than 16 GB, stop or delete them first.

## The walk

### 1. Read docs/08 · How Minikube works inside

Open [docs/08](../docs/08-minikube-internals.md). The one idea to keep: **the node is a container.** Inside it runs
the same things you installed by hand in chapter 02–03 (containerd, the kubelet, and kubeadm builds the control plane).
Everything you learned still applies; Minikube just does the preparation for you.

```text
 your computer
 └── Docker
     └── container "minikube"  (= the node)
         ├── containerd, kubelet
         └── etcd, API server, scheduler, controller manager (static Pods, as in kubeadm)
```

### 2. The lesson, Steps 1–4

Open [minikube/README.md](../minikube/README.md) and run **Steps 1–4**: install, `minikube start`, verify, test
workload.

What to watch for:

- `minikube start` ends by telling you kubectl now uses the cluster **minikube**. That is a new **context** in your
  `~/.kube/config`. In our CI run, the first `minikube start` took 35 s on a GitHub-hosted runner;
  on a laptop with a slow connection the first start takes longer because the base image is downloaded once.
- `kubectl get nodes` shows **one** node with the role `control-plane`, and your Pods run on it. Unlike the kubeadm
  cluster, Minikube does not taint its only node. Ask yourself why (one node: there is nowhere else to run Pods).
- In `kubectl get pods -A` you recognise etcd, the API server, the scheduler, the controller manager, CoreDNS and
  kube-proxy from chapter 03, plus `storage-provisioner`.
- "The node is a container" section: `docker ps` shows the container, and `minikube ssh -- sudo crictl ps` shows the
  Kubernetes containers inside it. `crictl` again, exactly as on a kubeadm node.
- On Windows and macOS, `minikube service web --url` opens a tunnel and keeps running. That is expected, not a hang.

### 3. Steps 5–7: add-ons, profiles, stop and start

Run **Steps 5–7**. The profile step creates a second, two-node cluster next to the first. Watch the context names and
`minikube profile list`. Then the lesson deletes it again. Step 7 shows that stopping keeps everything: your workload
comes back after `minikube start`, because it is stored in etcd inside the node container.

### 4. Troubleshooting 08 · Insufficient resources

Run [troubleshooting/08](../troubleshooting/08-insufficient-resources.md) on this cluster. Two parts:

- **Part A:** a cluster that is refused because the machine is too small. Read the error message; it gives the minimum.
- **Part B:** a Pod that asks for more CPU than the node has. It stays `Pending`, and there are no logs because no
  container was ever started. The answer is in the Pod's **Events**: `Insufficient cpu`. The scheduler counts
  **requests**, not real usage.

### 5. Lab 02 and the YAML example

Do [labs/02 · test against an older Kubernetes version](../labs/02-minikube-installation.md) without opening the
solution. Then read [examples/nginx/README.md](../examples/nginx/README.md) and apply it: the same `web` app, but as
YAML files with health checks and resource requests, the way you keep workloads in Git at work.

Leave the Minikube cluster running until the end of chapter 09, or remove it now with
[minikube/cleanup.md](../minikube/cleanup.md).

## Expert commentary

- **Why it matters at work.** Developers test Helm charts and manifests on Minikube (or kind) before they open a pull
  request, and CI pipelines spin up a throwaway cluster per run. "Which context am I in?" is the question that prevents
  you from deleting something in the wrong cluster. Make `kubectl config current-context` a reflex.
- **Version skew.** kubectl v1.37 talking to a v1.36 cluster (lab 02) is supported: kubectl may be one minor version
  newer or older than the server. Two versions apart is asking for subtle trouble.
- **Common mistakes.** Too little memory for Docker Desktop; forgetting that a profile is a whole separate cluster;
  expecting the node IP to be reachable on Windows/macOS without `minikube service` or `minikube tunnel`.
- **What an interviewer asks.** "How do you test against several Kubernetes versions locally?" "A Pod is Pending. What
  do you check?" "What is the difference between resource requests and limits?"

## Checkpoint

You are done when:

- [ ] `minikube start` and `minikube delete` hold no surprises for you
- [ ] you can explain where the control plane runs in Minikube
- [ ] you diagnosed the `Pending` Pod from its Events, and fixed it by changing its request
- [ ] lab 02 is done: two profiles, two versions, and you always knew which one kubectl used
- [ ] you applied `examples/nginx` and understand every field in `deployment.yaml`

Next: [07 · MicroK8s](07-microk8s.md)
