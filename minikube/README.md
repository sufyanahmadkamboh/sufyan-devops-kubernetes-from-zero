# Minikube · Kubernetes on your own computer

> **Time:** about 30 minutes · **You need:** Docker (Docker Desktop on Windows/macOS, Docker Engine on Linux), 2 CPUs
> and 4 GB of free memory, and the architecture from [docs/02](../docs/02-kubernetes-architecture.md).

## 1. What is it?

Minikube runs a complete Kubernetes cluster **on your computer**, inside a container (or a small VM), with one command.
It is maintained by the Kubernetes project.

## 2. Why does it exist?

Developers and learners need a real Kubernetes API to try things against, without machines, cloud accounts or an
afternoon of setup. Minikube creates one in a couple of minutes and deletes it just as fast.

## 3. When should I use it?

- learning Kubernetes and practising `kubectl`
- developing and testing applications and manifests locally before they go to a shared cluster
- trying add-ons (ingress, metrics-server, dashboard) safely

**Not** for production: everything runs on one machine, usually your laptop.

## 4. What do I need before starting?

| Item | Check |
|---|---|
| Docker running (Minikube's "docker driver" runs the cluster inside a container) | `docker version` |
| 2 CPUs, 4 GB RAM free, 20 GB disk | Minikube refuses to start with too little memory (we prove that below) |
| kubectl (installed below) | `kubectl version --client` |

## 5. What are we building?

```text
   Your computer
   ┌───────────────────────────────────────────────────────────┐
   │  Docker                                                   │
   │  ┌─────────────────────────────────────────────────────┐  │
   │  │ container "minikube"  =  one Kubernetes node        │  │
   │  │   control plane: API server, etcd, scheduler,       │  │
   │  │                  controller manager                 │  │
   │  │   kubelet + container runtime  ── your Pods ──      │  │
   │  └─────────────────────────────────────────────────────┘  │
   │       ▲                                                    │
   │  kubectl (context "minikube")                              │
   └───────────────────────────────────────────────────────────┘
```

One node that is control plane **and** worker at the same time. Under the hood, Minikube uses kubeadm to set it up.

**Versions tested here:** Minikube v1.39.0 with its default Kubernetes version, kubectl v1.37.1, Docker driver on
Ubuntu 24.04. The Windows and macOS install commands are tested on Windows and macOS machines.

---

## Step 1 · Install Minikube and kubectl

### Linux (x86-64)

<!-- test: contains=v1.39.0; output -->
```bash
curl -fsSLO https://github.com/kubernetes/minikube/releases/download/v1.39.0/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube && rm minikube-linux-amd64
minikube version
```

```text
minikube version: v1.39.0
commit: 7a9f6a841470a207de8cf4bafcccee0969d8ba10
```

kubectl is the client you use for **every** cluster in this repository, so install it on its own (Minikube can also
download one: `minikube kubectl -- get pods`):

<!-- test: contains=v1.37.1 -->
```bash
curl -fsSLO "https://dl.k8s.io/release/v1.37.1/bin/linux/amd64/kubectl"
sudo install -m 0755 kubectl /usr/local/bin/kubectl && rm kubectl
kubectl version --client
```

### Windows (PowerShell) and macOS

The official commands, tested on Windows and macOS machines in this repository's CI:

```text
# Windows (PowerShell): Minikube and kubectl
winget install --exact --id Kubernetes.minikube
winget install --exact --id Kubernetes.kubectl

# macOS (Homebrew)
brew install minikube kubectl
```

Then open a new terminal and run `minikube version`.

## Step 2 · Start the cluster

<!-- test: contains=Server; output=head:3 -->
```bash
docker version --format 'Client {{.Client.Version}} · Server {{.Server.Version}}'
```

```text
Client 28.0.4 · Server 28.0.4
```

`minikube start` downloads a Kubernetes base image (the first time only), creates a container named `minikube`, runs
kubeadm inside it, and sets your kubectl to the new cluster:

<!-- test: timeout=900; contains=Done; output=tail:8 -->
```bash
minikube start --driver=docker --cpus=2 --memory=4096
```

```text
...
* Pulling base image v0.0.51 ...
* Downloading Kubernetes v1.37.0 preload ...
    > gcr.io/k8s-minikube/kicbase:  1.60 KiB / 507.61 MiB [>____] 0.00% ? p/s ?    > gcr.io/k8s-minikube/kicbase:  637.92 KiB / 507.61 MiB [>__] 0.12% ? p/s ?    > gcr.io/k8s-minikube/kicbase:  22.41 MiB / 507.61 MiB [>___] 4.41% ? p/s ?    > gcr.io/k8s-minikube/kicbase:  64.49 MiB / 507.61 MiB  12.70% 107.45 MiB p    > gcr.io/k8s-minikube/kicbase:  107.14 MiB / 507.61 MiB  21.11% 107.45 MiB     > gcr.io/k8s-minikube/kicbase:  149.48 MiB / 507.61 MiB  29.45% 107.45 MiB     > gcr.io/k8s-minikube/kicbase:  192.44 MiB / 507.61 MiB  37.91% 114.29 MiB     > gcr.io/k8s-minikube/kicbase:  234.87 MiB / 507.61 MiB  46.27% 114.29 MiB     > gcr.io/k8s-minikube/kicbase:  278.01 MiB / 507.61 MiB  54.77% 114.29 MiB     > gcr.io/k8s-minikube/kicbase:  320.20 MiB / 507.61 MiB  63.08% 120.63 MiB     > gcr.io/k8s-minikube/kicbase:  362.32 MiB / 507.61 MiB  71.38% 120.63 MiB     > gcr.io/k8s-minikube/kicbase:  405.66 MiB / 507.61 MiB  79.92% 120.63 MiB     > gcr.io/k8s-minikube/kicbase:  447.77 MiB / 507.61 MiB  88.21% 126.59 MiB     > gcr.io/k8s-minikube/kicbase:  490.85 MiB / 507.61 MiB  96.70% 126.59 MiB     > gcr.io/k8s-minikube/kicbase:  507.60 MiB / 507.61 MiB  100.00% 189.50 MiB* Preparing Kubernetes v1.37.0 on containerd 2.3.4 ...
* Configuring CNI (Container Networking Interface) ...
* Verifying Kubernetes components...
  - Using image gcr.io/k8s-minikube/storage-provisioner:v5
* Enabled addons: storage-provisioner, default-storageclass
* Done! kubectl is now configured to use "minikube" cluster and "default" namespace by default
```

The last line matters: kubectl is now configured to use the cluster **minikube**. That happened through a *context* in
your kubeconfig file (`~/.kube/config`):

<!-- test: contains=minikube; output -->
```bash
kubectl config current-context
```

```text
minikube
```

## Step 3 · Verify the cluster

<!-- test: contains=Running; output -->
```bash
minikube status
```

```text
minikube
type: Control Plane
host: Running
kubelet: Running
apiserver: Running
kubeconfig: Configured
```

`host` is the container, `kubelet` and `apiserver` the Kubernetes components, `kubeconfig` whether kubectl points at it.

<!-- test: retry=30; contains=Ready; absent=NotReady; output -->
```bash
kubectl get nodes -o wide
```

```text
NAME       STATUS   ROLES           AGE   VERSION   INTERNAL-IP    EXTERNAL-IP   OS-IMAGE                         KERNEL-VERSION              CONTAINER-RUNTIME
minikube   Ready    control-plane   23s   v1.37.0   192.168.49.2   <none>        Debian GNU/Linux 12 (bookworm)   6.17.0-1022-azure (amd64)   containerd://2.3.4
```

One node named `minikube` with the role `control-plane`. It runs your workloads too: unlike the kubeadm lab, Minikube
does not taint it.

<!-- test: retry=30; absent=Pending; output -->
```bash
kubectl get pods -A
```

```text
NAMESPACE     NAME                               READY   STATUS    RESTARTS   AGE
kube-system   coredns-559f6c778d-vtgvt           1/1     Running   0          14s
kube-system   etcd-minikube                      1/1     Running   0          20s
kube-system   kindnet-96zsk                      1/1     Running   0          14s
kube-system   kube-apiserver-minikube            1/1     Running   0          20s
kube-system   kube-controller-manager-minikube   1/1     Running   0          20s
kube-system   kube-proxy-dpftw                   1/1     Running   0          14s
kube-system   kube-scheduler-minikube            1/1     Running   0          21s
kube-system   storage-provisioner                1/1     Running   0          19s
```

The same components as in the kubeadm cluster (etcd, API server, scheduler, controller manager, CoreDNS, kube-proxy),
plus `storage-provisioner`, Minikube's add-on that gives you persistent volumes out of the box.

<!-- test: contains=is running at; output -->
```bash
kubectl cluster-info
kubectl get namespaces
```

```text
Kubernetes control plane is running at https://192.168.49.2:8443
CoreDNS is running at https://192.168.49.2:8443/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy

To further debug and diagnose cluster problems, use 'kubectl cluster-info dump'.
NAME              STATUS   AGE
default           Active   22s
kube-node-lease   Active   22s
kube-public       Active   22s
kube-system       Active   22s
```

### The node is a container

Minikube's node is a Docker container. Look at it, and inside it:

<!-- test: contains=minikube; output -->
```bash
docker ps --filter name=minikube --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}'
minikube ip
```

```text
NAMES      IMAGE                                 STATUS
minikube   gcr.io/k8s-minikube/kicbase:v0.0.51   Up 31 seconds
192.168.49.2
```

<!-- test: contains=kube-apiserver; output=head:8 -->
```bash
minikube ssh -- sudo crictl ps --name 'kube-' -o table
```

```text
CONTAINER           IMAGE               CREATED             STATE               NAME                      ATTEMPT             POD ID              POD                                NAMESPACE
a98e08dc09f34       d6a28daf3e6b0       14 seconds ago      Running             kube-proxy                0                   2354edf1bf9fc       kube-proxy-dpftw                   kube-system
f1a93dcfdeab2       bec5f0e1e2eeb       24 seconds ago      Running             kube-apiserver            0                   4e695cd28c66c       kube-apiserver-minikube            kube-system
b0a86b760a6e9       364b3c3d9ec19       24 seconds ago      Running             kube-controller-manager   0                   a7677388e46d2       kube-controller-manager-minikube   kube-system
5962391319f3e       1fabf80a1273a       24 seconds ago      Running             kube-scheduler            0                   04fa3fb40573e       kube-scheduler-minikube            kube-system
```

`minikube ssh` opens a shell on the node; with `--` it runs one command. `crictl` talks to the container runtime
through the CRI, exactly as on a kubeadm node.

## Step 4 · A test workload

<!-- test: contains=deployment.apps/web created -->
```bash
kubectl create deployment web --image=nginx:1.30-alpine --replicas=2
kubectl expose deployment web --port=80 --type=NodePort
```

<!-- test: retry=60; contains=2/2; output -->
```bash
kubectl rollout status deployment/web --timeout=10s
kubectl get deployment,service web
```

```text
Waiting for deployment "web" rollout to finish: 0 of 2 updated replicas are available...
Waiting for deployment "web" rollout to finish: 1 of 2 updated replicas are available...
deployment "web" successfully rolled out
NAME                  READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/web   2/2     2            2           2s

NAME          TYPE       CLUSTER-IP      EXTERNAL-IP   PORT(S)        AGE
service/web   NodePort   10.99.103.237   <none>        80:31773/TCP   2s
```

`minikube service` prints a URL that reaches the NodePort from your computer:

<!-- test: retry=20; contains=Welcome to nginx; output -->
```bash
URL=$(minikube service web --url)
echo "$URL"
curl -s "$URL" | grep -o '<title>.*</title>'
```

```text
http://192.168.49.2:31773
<title>Welcome to nginx!</title>
```

> On Windows and macOS with the Docker driver, the node's IP is not reachable from your computer directly, so
> `minikube service web --url` opens a tunnel and keeps running; leave that terminal open and use the URL in a browser.

## Step 5 · Add-ons and the dashboard

Add-ons are optional components Minikube can install for you:

<!-- test: contains=metrics-server; output=head:12 -->
```bash
minikube addons list | grep -E 'ADDON NAME|dashboard|ingress |metrics-server|storage-provisioner'
```

```text
│         ADDON NAME          │ PROFILE  │   STATUS   │               MAINTAINER               │
│ dashboard                   │ minikube │ disabled   │ Kubernetes                             │
│ ingress                     │ minikube │ disabled   │ Kubernetes                             │
│ metrics-server              │ minikube │ disabled   │ Kubernetes                             │
│ storage-provisioner         │ minikube │ enabled ✅ │ minikube                               │
│ storage-provisioner-rancher │ minikube │ disabled   │ 3rd party (Rancher)                    │
```

<!-- test: contains=enabled -->
```bash
minikube addons enable metrics-server
```

<!-- test: retry=60; contains=minikube; output -->
```bash
kubectl top nodes
```

```text
NAME       CPU(cores)   CPU(%)   MEMORY(bytes)   MEMORY(%)   
minikube   132m         3%       673Mi           4%          
```

The web dashboard opens in your browser with `minikube dashboard` (it keeps running until you press Ctrl+C):

<!-- test: skip -->
```bash
minikube dashboard
```

## Step 6 · Profiles: more than one cluster, and more than one node

A **profile** is a separately named Minikube cluster. Each gets its own kubectl context. Let's start a second cluster
with **two nodes**, to see a worker:

<!-- test: timeout=900; contains=Done -->
```bash
minikube start -p multinode --nodes 2 --driver=docker --cpus=2 --memory=2200
```

<!-- test: retry=60; contains=multinode-m02; absent=NotReady; output -->
```bash
kubectl --context multinode get nodes
minikube profile list
```

```text
NAME            STATUS   ROLES           AGE   VERSION
multinode       Ready    control-plane   32s   v1.37.0
multinode-m02   Ready    <none>          16s   v1.37.0
┌───────────┬────────┬────────────┬──────────────┬─────────┬────────┬───────┬────────────────┬────────────────────┐
│  PROFILE  │ DRIVER │  RUNTIME   │      IP      │ VERSION │ STATUS │ NODES │ ACTIVE PROFILE │ ACTIVE KUBECONTEXT │
├───────────┼────────┼────────────┼──────────────┼─────────┼────────┼───────┼────────────────┼────────────────────┤
│ minikube  │ docker │ containerd │ 192.168.49.2 │ v1.37.0 │ OK     │ 1     │ *              │                    │
│ multinode │ docker │ containerd │ 192.168.58.2 │ v1.37.0 │ OK     │ 2     │                │ *                  │
└───────────┴────────┴────────────┴──────────────┴─────────┴────────┴───────┴────────────────┴────────────────────┘
```

`multinode-m02` is a worker node, a second container. `minikube profile list` shows both clusters. Delete the extra one:

```text
⚠️ DESTRUCTIVE COMMAND · deletes the "multinode" cluster and everything in it.
```

<!-- test: timeout=300; contains=Removed -->
```bash
minikube delete -p multinode
```

## Step 7 · Stop and start

Stopping keeps everything (your Deployment, Service, images) and frees the memory:

<!-- test: timeout=300; contains=Stopped; output -->
```bash
minikube stop
minikube status || true
```

```text
* Stopping node "minikube"  ...
* Powering off "minikube" via SSH ...
* 1 node stopped.
minikube
type: Control Plane
host: Stopped
kubelet: Stopped
apiserver: Stopped
kubeconfig: Stopped
```

<!-- test: timeout=900; contains=Done -->
```bash
minikube start
```

<!-- test: retry=60; contains=2/2 -->
```bash
kubectl get deployment web
```

The workload came back on its own, because it was stored in etcd, inside the node container.

## Common errors

| Symptom | Cause | Fix |
|---|---|---|
| `Exiting due to RSRC_INSUFFICIENT_REQ_MEMORY` | asked for less memory than Minikube needs | give it at least about 1.8 GB (see [troubleshooting/08](../troubleshooting/08-insufficient-resources.md)) |
| `Exiting due to PROVIDER_DOCKER_NOT_RUNNING` | Docker is not running | start Docker Desktop / `sudo systemctl start docker` |
| kubectl talks to the wrong cluster | another context is current | `kubectl config use-context minikube` |
| `minikube service --url` never returns on Windows/macOS | it is running a tunnel on purpose | leave it open, use the URL |

## Cleanup

When you are done (after the troubleshooting lab [08](../troubleshooting/08-insufficient-resources.md), which uses this
cluster): [minikube/cleanup.md](cleanup.md).

## Practical challenge

[labs/02-minikube-installation.md](../labs/02-minikube-installation.md)

## Real-world usage

Developers use Minikube (or its cousins kind and k3d) to run and test their services against a real Kubernetes API
on their laptop, trainers use it for classes, and some teams use it in CI to test Helm charts or manifests. You will not
meet it in production.

## Key takeaways

- One command gives you a full, single-node cluster in a container; `minikube delete` removes it completely.
- It is the same Kubernetes: same components, same kubectl, configured through a kubeconfig context.
- Profiles give you several clusters; `--nodes` adds workers; add-ons install common extras.
- It needs real resources: about 2 CPUs and 2 GB of memory at the very least.

Next: [MicroK8s](../microk8s/README.md)
