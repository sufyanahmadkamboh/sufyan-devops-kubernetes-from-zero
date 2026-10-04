# MicroK8s · Lightweight Kubernetes in one package

> **Time:** about 30 minutes · **You need:** one Ubuntu 24.04 machine (here: a Multipass VM with 2 CPUs and 4 GB RAM)
> and the architecture from [docs/02](../docs/02-kubernetes-architecture.md).

## 1. What is it?

MicroK8s is a complete Kubernetes distribution from Canonical, packaged as a single **snap**. One command installs the
control plane, the kubelet, a container runtime (containerd), a CNI (Calico) and CoreDNS, all already configured.

## 2. Why does it exist?

A kubeadm cluster takes a dozen preparation steps on every machine. MicroK8s ships all of that pre-assembled and keeps
itself updated through snap channels, which makes Kubernetes practical on small machines: a workstation, a lab server,
an edge device, a Raspberry Pi, a CI machine.

## 3. When should I use it?

- a quick, real Kubernetes on one Linux machine (or a small cluster of a few machines with `microk8s add-node`)
- edge and IoT devices, appliances, labs, CI
- learning, when you want a Linux-native cluster without a VM per node

How it differs:

| | kubeadm | Minikube | MicroK8s |
|---|---|---|---|
| Installs | only the Kubernetes parts; you prepare runtime, CNI, OS | a cluster inside a container or VM on your laptop | everything in one snap, directly on the Linux host |
| Typical place | servers you manage | your laptop | Linux machines, edge devices, labs |
| Multi-node | yes (kubeadm join) | yes, all on one laptop | yes (`microk8s add-node`) |
| Updates | you upgrade with kubeadm | delete and recreate | snap channels (e.g. `1.36/stable`) |

## 4. What do I need before starting?

A Linux machine with snap (Ubuntu has it), 2 CPUs, 4 GB RAM, 20 GB disk, internet access. On Windows or macOS, create an
Ubuntu VM first (below, with Multipass).

## 5. What are we building?

```text
   Ubuntu 24.04 (k8s-micro)
   ┌──────────────────────────────────────────────────────────────┐
   │  snap "microk8s"                                             │
   │  ┌────────────────────────────────────────────────────────┐  │
   │  │ kubelite: API server, scheduler, controller manager,   │  │
   │  │           kubelet, kube-proxy (one process)            │  │
   │  │ datastore: dqlite (instead of etcd)                    │  │
   │  │ containerd · Calico CNI · CoreDNS                      │  │
   │  └────────────────────────────────────────────────────────┘  │
   │   microk8s kubectl ...                                       │
   └──────────────────────────────────────────────────────────────┘
```

Two differences from kubeadm worth knowing: MicroK8s runs the Kubernetes components inside one process called
**kubelite**, and stores cluster state in **dqlite**, a distributed SQLite, instead of etcd.

**Versions tested here:** MicroK8s from the `1.36/stable` channel (the newest stable track when this lab was built;
MicroK8s publishes new Kubernetes versions on its own schedule) on Ubuntu 24.04.

---

## Step 1 · Create the machine (on your computer)

<!-- test: timeout=900 -->
```bash
multipass launch 24.04 --name k8s-micro --cpus 2 --memory 4G --disk 20G
```

The following steps run on **🖥️ k8s-micro** (`multipass shell k8s-micro`).

## Step 2 · Install MicroK8s

`--classic` gives the snap normal access to the system (Kubernetes needs it); `--channel` picks the Kubernetes version
track. Pinning a channel means you choose when to move to the next minor version.

<!-- test: on=k8s-micro; timeout=900; contains=installed -->
```bash
sudo snap install microk8s --classic --channel=1.36/stable
```

MicroK8s commands need root, or membership in the `microk8s` group. Add your user, and give it the `~/.kube` folder
MicroK8s writes to:

<!-- test: on=k8s-micro -->
```bash
sudo usermod -a -G microk8s "$USER"
mkdir -p ~/.kube && chmod 0700 ~/.kube
```

Group membership only applies to **new** login sessions. Log out and back in (`exit`, then `multipass shell k8s-micro`),
or start a shell with the new group:

<!-- test: skip -->
```bash
newgrp microk8s
```

<!-- test: on=k8s-micro; contains=microk8s -->
```bash
groups
```

## Step 3 · Check the status

<!-- test: on=k8s-micro; timeout=600; contains=microk8s is running; output=head:12 -->
```bash
microk8s status --wait-ready
```

```text
microk8s is running
high-availability: no
  datastore master nodes: 127.0.0.1:19001
  datastore standby nodes: none
addons:
  enabled:
    dns                  # (core) CoreDNS
    ha-cluster           # (core) Configure high availability on the current node
    helm                 # (core) Helm - the package manager for Kubernetes
    helm3                # (core) Helm 3 - the package manager for Kubernetes
  disabled:
    cert-manager         # (core) Cloud native certificate management
...
```

`--wait-ready` waits until Kubernetes is up. The output lists the **add-ons**: enabled ones (for example `dns` for
CoreDNS) and the many that are one command away.

## Step 4 · kubectl, the MicroK8s way

MicroK8s bundles its own kubectl, matched to its Kubernetes version:

<!-- test: on=k8s-micro; retry=30; contains=Ready; absent=NotReady; output -->
```bash
microk8s kubectl get nodes -o wide
```

```text
NAME        STATUS   ROLES    AGE   VERSION   INTERNAL-IP      EXTERNAL-IP   OS-IMAGE             KERNEL-VERSION              CONTAINER-RUNTIME
k8s-micro   Ready    <none>   16s   v1.36.2   10.160.245.156   <none>        Ubuntu 24.04.5 LTS   6.8.0-142-generic (amd64)   containerd://2.2.3
```

<!-- test: on=k8s-micro; retry=60; absent=Pending; absent=ContainerCreating; output -->
```bash
microk8s kubectl get pods -A
```

```text
NAMESPACE     NAME                                       READY   STATUS    RESTARTS   AGE
kube-system   calico-kube-controllers-8496b98c8c-z66hk   1/1     Running   0          27s
kube-system   calico-node-l4m5p                          1/1     Running   0          27s
kube-system   coredns-84dbc6f76d-6xqbq                   1/1     Running   0          27s
```

Notice what is **not** there: no `kube-apiserver` or `etcd` Pods. Those run inside the `kubelite` service, not as Pods.
What you see is Calico (the CNI) and CoreDNS. The services themselves are systemd units managed by the snap:

<!-- test: on=k8s-micro; contains=kubelite; output -->
```bash
systemctl list-units 'snap.microk8s.*' --no-legend --plain | awk '{print $1, $3, $4}'
```

```text
snap.microk8s.daemon-apiserver-kicker.service active running
snap.microk8s.daemon-cluster-agent.service active running
snap.microk8s.daemon-containerd.service active running
snap.microk8s.daemon-k8s-dqlite.service active running
snap.microk8s.daemon-kubelite.service active running
```

Typing `microk8s kubectl` gets long. A snap alias makes plain `kubectl` work. (If you already have another kubectl on
this machine, skip this and keep the prefix, or export the config with `microk8s config > ~/.kube/config`.)

<!-- test: on=k8s-micro; contains=Added -->
```bash
sudo snap alias microk8s.kubectl kubectl
```

<!-- test: on=k8s-micro; contains=is running at; output -->
```bash
kubectl cluster-info
kubectl get namespaces
```

```text
Kubernetes control plane is running at https://127.0.0.1:16443
CoreDNS is running at https://127.0.0.1:16443/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy

To further debug and diagnose cluster problems, use 'kubectl cluster-info dump'.
NAME              STATUS   AGE
default           Active   36s
kube-node-lease   Active   36s
kube-public       Active   36s
kube-system       Active   36s
```

## Step 5 · Add-ons

Add-ons are pre-packaged components. Let's enable two common ones: local persistent storage and the metrics server:

<!-- test: on=k8s-micro; timeout=600; contains=enabled -->
```bash
microk8s enable hostpath-storage
microk8s enable metrics-server
```

<!-- test: on=k8s-micro; contains=hostpath-storage; output -->
```bash
microk8s status --format short | grep -E 'enabled' | head -8
```

```text
core/dns: enabled
core/ha-cluster: enabled
core/helm: enabled
core/helm3: enabled
core/hostpath-storage: enabled
core/metrics-server: enabled
core/storage: enabled
```

<!-- test: on=k8s-micro; retry=60; contains=k8s-micro; output -->
```bash
kubectl top nodes
```

```text
NAME        CPU(cores)   CPU(%)   MEMORY(bytes)   MEMORY(%)   
k8s-micro   444m         22%      1169Mi          31%         
```

## Step 6 · A test workload

<!-- test: on=k8s-micro; contains=deployment.apps/web created -->
```bash
kubectl create deployment web --image=nginx:1.30-alpine --replicas=2
kubectl expose deployment web --port=80 --type=NodePort
```

<!-- test: on=k8s-micro; retry=60; contains=2/2; output -->
```bash
kubectl rollout status deployment/web --timeout=10s
kubectl get deployment,service web
```

```text
Waiting for deployment "web" rollout to finish: 0 of 2 updated replicas are available...
Waiting for deployment "web" rollout to finish: 1 of 2 updated replicas are available...
deployment "web" successfully rolled out
NAME                  READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/web   2/2     2            2           4s

NAME          TYPE       CLUSTER-IP       EXTERNAL-IP   PORT(S)        AGE
service/web   NodePort   10.152.183.178   <none>        80:30398/TCP   4s
```

<!-- test: on=k8s-micro; retry=30; contains=Welcome to nginx; output -->
```bash
NODE_PORT=$(kubectl get service web -o jsonpath='{.spec.ports[0].nodePort}')
curl -s "http://127.0.0.1:$NODE_PORT" | grep -o '<title>.*</title>'
```

```text
<title>Welcome to nginx!</title>
```

## Step 7 · Stop, start and inspect

`microk8s stop` stops every Kubernetes service on the machine (useful on a laptop or an edge device); `start` brings
them back with all objects intact:

<!-- test: on=k8s-micro; timeout=300; contains=Stopped -->
```bash
microk8s stop
```

<!-- test: on=k8s-micro; contains=not running -->
```bash
microk8s status
```

<!-- test: on=k8s-micro; timeout=600; contains=microk8s is running -->
```bash
microk8s start
microk8s status --wait-ready | head -1
```

<!-- test: on=k8s-micro; retry=60; contains=2/2 -->
```bash
kubectl get deployment web
```

When something is wrong, `microk8s inspect` checks the services, the network settings and the logs, and packs them into
a report:

<!-- test: on=k8s-micro; timeout=600; contains=Inspecting; output=head:12 -->
```bash
sudo microk8s inspect
```

```text
Inspecting system
Inspecting Certificates
Inspecting services
  Service snap.microk8s.daemon-cluster-agent is running
  Service snap.microk8s.daemon-containerd is running
  Service snap.microk8s.daemon-kubelite is running
  Service snap.microk8s.daemon-k8s-dqlite is running
  Service snap.microk8s.daemon-apiserver-kicker is running
  Copy service arguments to the final report tarball
Inspecting AppArmor configuration
Gathering system information
  Copy processes list to the final report tarball
...
```

## Common errors

| Symptom | Cause | Fix |
|---|---|---|
| `Insufficient permissions to access MicroK8s` | your user is not in the `microk8s` group yet | `sudo usermod -a -G microk8s $USER`, then log out and in |
| `microk8s is not running` | services stopped | `microk8s start`, then `sudo microk8s inspect` |
| Pods `Pending` with storage | no storage add-on | `microk8s enable hostpath-storage` |
| plain `kubectl` talks to another cluster | another kubectl is first in your PATH | use `microk8s kubectl` |

## Cleanup

When you are done (after the [practical challenge](../labs/03-microk8s-installation.md), which uses this
cluster): [microk8s/cleanup.md](cleanup.md).

## Practical challenge

[labs/03-microk8s-installation.md](../labs/03-microk8s-installation.md)

## Real-world usage

MicroK8s shows up on edge and IoT devices, in labs and CI pipelines, on developer workstations, and in smaller on-site
deployments where a full kubeadm setup or a cloud service would be overkill. For large production clusters, teams more
often choose kubeadm-based tooling or a managed service; MicroK8s production use depends on the requirements.

## Key takeaways

- One snap installs a full Kubernetes: runtime, CNI, CoreDNS, control plane (as `kubelite`), datastore (`dqlite`).
- Users need the `microk8s` group; group changes need a new login session.
- Add-ons (`microk8s enable ...`) install common components in one step.
- `microk8s status`, `microk8s inspect` and `systemctl` are your first troubleshooting tools.

Next: [Amazon EKS](../eks/README.md)
