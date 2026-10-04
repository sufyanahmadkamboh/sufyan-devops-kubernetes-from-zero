# kubeadm · A real two-node Kubernetes cluster on Ubuntu

> **Time:** about 60 minutes · **You need:** a computer with 8 GB of RAM or more, [Multipass](https://canonical.com/multipass/install)
> to create two Ubuntu virtual machines, and the concepts from [docs/02](../docs/02-kubernetes-architecture.md) and
> [docs/03](../docs/03-installation-prerequisites.md).

## 1. What is it?

`kubeadm` is the official Kubernetes tool that turns ordinary Linux machines into a cluster. It does not create the
machines and it does not install the container runtime: **you** prepare the machines, and kubeadm does the Kubernetes
part (certificates, the control-plane components, the join process).

## 2. Why does it exist?

Kubernetes is several programs that must be configured to trust each other: an API server, etcd, a scheduler, a
controller manager, and a kubelet on every machine. Doing that by hand means creating a certificate authority, a dozen
certificates and config files. kubeadm automates exactly that, in the way the Kubernetes project recommends.

## 3. When should I use it?

- to **learn how a cluster really works** (this lab), and for Kubernetes administrator certifications
- for **self-managed clusters**: on-premises, bare metal, private data centres, anywhere there is no managed service
- as the engine inside other tools (kind and minikube use kubeadm internally)

For a laptop playground, [Minikube](../minikube/README.md) is quicker. For production in AWS, [EKS](../eks/README.md)
takes the control plane off your hands.

## 4. What do I need before starting?

| Item | Why |
|---|---|
| Two Ubuntu 24.04 LTS machines (here: Multipass VMs) | one control plane, one worker |
| 2 CPUs and 4 GB RAM for the control plane, 2 CPUs and 3 GB for the worker | kubeadm refuses to set up a control plane with fewer than 2 CPUs |
| Network connectivity between them | the worker must reach the API server on TCP 6443 |
| Internet access | packages and container images are downloaded |

## 5. What are we building?

```text
   Your computer (Multipass)
   ┌────────────────────────────────────────────────────────────────────────────┐
   │  k8s-cp  (control plane)                       k8s-worker                   │
   │  ┌───────────────────────────────┐             ┌──────────────────────────┐ │
   │  │ kube-apiserver   :6443  ◄─────┼─────────────┤ kubelet                  │ │
   │  │ etcd             :2379        │             │ kube-proxy               │ │
   │  │ kube-scheduler                │             │ containerd (runtime)     │ │
   │  │ kube-controller-manager       │             │ Flannel (pod network)    │ │
   │  │ kubelet + containerd + Flannel│             │ ── your Pods run here ── │ │
   │  └───────────────────────────────┘             └──────────────────────────┘ │
   └────────────────────────────────────────────────────────────────────────────┘
```

**This is a learning cluster, not a production design.** Production needs several control-plane nodes behind a load
balancer (high availability), more workers, persistent storage, backups of etcd, security hardening and monitoring.
See [docs/05](../docs/05-kubeadm-installation.md#production-is-different).

The installation, stage by stage:

```text
 Prepare Ubuntu ──► Container runtime ──► kubeadm, kubelet, kubectl ──► kubeadm init ──► kubeconfig
 (swap, modules,     (containerd 2.x,        (pkgs.k8s.io, v1.37)          (control plane)   (kubectl access)
  sysctl)             systemd cgroups)                                                            │
                                                                                                  ▼
                        Working cluster ◄── verify ◄── kubeadm join (worker) ◄── CNI (Flannel pod network)
```

**Versions used and tested here:** Ubuntu 24.04 LTS, Kubernetes v1.37 (packages from `pkgs.k8s.io`), containerd 2.x
from Docker's apt repository, Flannel v0.28.9.

---

## Step 1 · Create the two machines

On **your computer**, with Multipass installed:

<!-- test: timeout=900 -->
```bash
multipass launch 24.04 --name k8s-cp --cpus 2 --memory 4G --disk 20G
multipass launch 24.04 --name k8s-worker --cpus 2 --memory 3G --disk 20G
```

<!-- test: contains=k8s-cp; contains=k8s-worker -->
```bash
multipass list
```

Each machine is a full Ubuntu 24.04 virtual machine with its own IP address. Throughout this guide, a block marked
**🖥️ on k8s-cp** runs on the control plane, **🖥️ on k8s-worker** on the worker, and **🖥️ on both** on each of them.
Open a shell on a machine with `multipass shell k8s-cp` (type `exit` to leave):

<!-- test: skip -->
```bash
multipass shell k8s-cp
```

## Step 2 · Prepare Ubuntu (🖥️ on both)

### 2a. Check what makes each machine unique

Kubernetes identifies nodes by hostname, and some components rely on unique MAC addresses and `product_uuid`. Clones
of the same VM image sometimes share them, which breaks the cluster in confusing ways. Check them now:

<!-- test: on=k8s-cp+k8s-worker; output -->
```bash
hostname
ip -4 -brief address show scope global
sudo cat /sys/class/dmi/id/product_uuid
```

```text
[k8s-cp]
k8s-cp
enp5s0           UP             10.97.7.168/24 metric 100 
775aed78-3f05-47f8-bc8b-11ebd618b50f
[k8s-worker]
k8s-worker
enp5s0           UP             10.97.7.171/24 metric 100 
5d6a82b0-ba15-4bfe-b0b4-81340689c146
```

Different hostnames, different addresses, different UUIDs: good.

### 2b. Swap

By default the kubelet refuses to start when swap is on: the scheduler's memory decisions assume that what a Pod is
given is real memory. (Newer Kubernetes can be configured to tolerate swap, but that is an advanced, opt-in setup.)
Cloud and Multipass images usually have no swap; turn it off anyway and keep it off after a reboot:

<!-- test: on=k8s-cp+k8s-worker -->
```bash
sudo swapoff -a
sudo sed -i '/\sswap\s/ s/^/#/' /etc/fstab
swapon --show
```

`swapon --show` prints nothing: no swap is active.

### 2c. Kernel modules and network settings

Pod traffic crosses Linux bridges and is routed between machines. Two kernel modules and three settings make that work:

- `overlay`: the filesystem driver containerd uses to stack image layers
- `br_netfilter`: lets iptables see traffic crossing a bridge (kube-proxy and Flannel rely on it)
- `net.ipv4.ip_forward = 1`: lets the machine forward packets for Pods (without it, Pod traffic stops at the node)
- `net.bridge.bridge-nf-call-iptables = 1` (and the IPv6 one): send bridged traffic through iptables

<!-- test: on=k8s-cp+k8s-worker -->
```bash
cat <<'EOF' | sudo tee /etc/modules-load.d/k8s.conf
overlay
br_netfilter
EOF
sudo modprobe overlay
sudo modprobe br_netfilter

cat <<'EOF' | sudo tee /etc/sysctl.d/k8s.conf
net.ipv4.ip_forward = 1
net.bridge.bridge-nf-call-iptables = 1
net.bridge.bridge-nf-call-ip6tables = 1
EOF
sudo sysctl --system > /dev/null
```

The files in `/etc/modules-load.d/` and `/etc/sysctl.d/` make the settings survive a reboot. Verify:

<!-- test: on=k8s-cp+k8s-worker; contains=net.ipv4.ip_forward = 1; contains=br_netfilter; output -->
```bash
lsmod | grep -E '^(overlay|br_netfilter)'
sysctl net.ipv4.ip_forward net.bridge.bridge-nf-call-iptables
```

```text
[k8s-cp]
br_netfilter           32768  0
overlay               212992  0
net.ipv4.ip_forward = 1
net.bridge.bridge-nf-call-iptables = 1
[k8s-worker]
br_netfilter           32768  0
overlay               212992  0
net.ipv4.ip_forward = 1
net.bridge.bridge-nf-call-iptables = 1
```

### 2d. Time, firewall and ports

Certificates have validity periods, so the clocks must agree. Ubuntu synchronises time with `systemd-timesyncd`:

<!-- test: on=k8s-cp+k8s-worker; contains=System clock synchronized: yes; retry=60 -->
```bash
timedatectl | grep -E 'synchronized|NTP service'
```

Kubernetes needs these ports open between the machines (Ubuntu's `ufw` firewall is inactive on these images; on a
real network, the firewall or cloud security group must allow them):

| Machine | Port | Used by |
|---|---|---|
| control plane | TCP 6443 | Kubernetes API server (everyone talks to it) |
| control plane | TCP 2379-2380 | etcd |
| control plane | TCP 10250, 10257, 10259 | kubelet, controller manager, scheduler |
| worker | TCP 10250 | kubelet API |
| worker | TCP 30000-32767 | NodePort Services |
| both | UDP 8472 | Flannel VXLAN (the pod network between nodes) |

<!-- test: on=k8s-cp+k8s-worker; contains=inactive -->
```bash
sudo ufw status
```

## Step 3 · Install the container runtime: containerd (🖥️ on both)

Kubernetes does not run containers itself. The kubelet asks a **container runtime** to do it, through the Container
Runtime Interface (CRI). We use **containerd 2.x** from Docker's official apt repository. Ubuntu 24.04's own package is
containerd 1.7, and the Kubernetes project has announced that kubelets after v1.37 will no longer work with containerd
1.x, so we start on 2.x.

```text
 kubelet ──CRI (gRPC on /run/containerd/containerd.sock)──► containerd ──► runc ──► containers
```

<!-- test: on=k8s-cp+k8s-worker; timeout=900 -->
```bash
sudo apt-get update -q
sudo apt-get install -y -q ca-certificates curl gpg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor --yes -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list
sudo apt-get update -q
sudo apt-get install -y -q containerd.io
```

The package ships a configuration made for Docker, **with the Kubernetes (CRI) plugin disabled**. Replace it with the
complete default configuration, then switch runc to the **systemd cgroup driver**. Ubuntu 24.04 uses cgroup v2 with
systemd as the init system, and the kubelet and the runtime must use the same driver:

<!-- test: on=k8s-cp+k8s-worker; contains=SystemdCgroup = true -->
```bash
containerd config default | sudo tee /etc/containerd/config.toml > /dev/null
sudo sed -i 's/SystemdCgroup = false/SystemdCgroup = true/' /etc/containerd/config.toml
grep -n 'SystemdCgroup' /etc/containerd/config.toml
sudo systemctl restart containerd
```

<!-- test: on=k8s-cp+k8s-worker; contains=active; output -->
```bash
containerd --version
systemctl is-active containerd
```

```text
[k8s-cp]
containerd containerd v2.3.6 ee2735368117d2eb259779949d5e75cdafec9761
active
[k8s-worker]
containerd containerd v2.3.6 ee2735368117d2eb259779949d5e75cdafec9761
active
```

## Step 4 · Install kubeadm, kubelet and kubectl (🖥️ on both)

| Tool | What it does | Where |
|---|---|---|
| `kubelet` | the agent on every node: starts Pods through containerd and reports back to the API server | every node |
| `kubeadm` | creates the cluster (`init`) and adds nodes (`join`) | every node |
| `kubectl` | the command-line client that talks to the API server | wherever you manage the cluster |

The Kubernetes project publishes packages at `pkgs.k8s.io`, one repository per minor version. This adds the v1.37
repository, installs the three tools and **holds** them, so a routine `apt upgrade` can never upgrade Kubernetes
underneath you (cluster upgrades follow their own procedure):

<!-- test: on=k8s-cp+k8s-worker; timeout=900 -->
```bash
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.37/deb/Release.key | sudo gpg --dearmor --yes -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.37/deb/ /' \
  | sudo tee /etc/apt/sources.list.d/kubernetes.list
sudo apt-get update -q
sudo apt-get install -y -q kubelet kubeadm kubectl cri-tools
sudo apt-mark hold kubelet kubeadm kubectl
sudo systemctl enable --now kubelet
```

<!-- test: on=k8s-cp; contains=v1.37; output -->
```bash
kubeadm version -o short
kubectl version --client
```

```text
v1.37.1
Client Version: v1.37.1
Kustomize Version: v5.8.1
```

At this point the kubelet restarts every few seconds. That is expected: it is waiting for `kubeadm init` or
`kubeadm join` to tell it what to do.

## Step 5 · Create the control plane: `kubeadm init` (🖥️ on k8s-cp)

`kubeadm init` does, in order:

1. **preflight checks** (CPUs, memory, swap, ports, container runtime), then pulls the control-plane images
2. creates a **certificate authority** and the certificates in `/etc/kubernetes/pki`
3. writes **kubeconfig files** for the admin, the kubelet, the controller manager and the scheduler
4. writes **static Pod manifests** to `/etc/kubernetes/manifests`: the kubelet starts the API server, etcd, the
   scheduler and the controller manager from these files
5. waits until the API server is healthy, then installs **CoreDNS** and **kube-proxy**, and creates a **join token**

`--pod-network-cidr` reserves the address range for Pods. `10.244.0.0/16` is the range Flannel expects by default.

<!-- test: on=k8s-cp; timeout=900; contains=Your Kubernetes control-plane has initialized successfully; output=tail:16 -->
```bash
sudo kubeadm init --pod-network-cidr=10.244.0.0/16
```

```text
...
  mkdir -p $HOME/.kube
  sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
  sudo chown $(id -u):$(id -g) $HOME/.kube/config

Alternatively, if you are the root user, you can run:

  export KUBECONFIG=/etc/kubernetes/admin.conf

You should now deploy a pod network to the cluster.
Run "kubectl apply -f [podnetwork].yaml" with one of the options listed at:
  https://kubernetes.io/docs/concepts/cluster-administration/addons/

Then you can join any number of worker nodes by running the following on each as root:

kubeadm join 10.97.7.168:6443 --token <bootstrap-token> \
	--discovery-token-ca-cert-hash sha256:a111e83695ca381b197dee40eb2fdc87bc6dee3db926ee8e94cc6be2c481522e 
```

Read the end of the output: it tells you the next three steps. First, give your normal user a kubeconfig, the file
that tells `kubectl` where the API server is and which certificate to log in with:

<!-- test: on=k8s-cp -->
```bash
mkdir -p "$HOME/.kube"
sudo cp /etc/kubernetes/admin.conf "$HOME/.kube/config"
sudo chown "$(id -u):$(id -g)" "$HOME/.kube/config"
```

> `admin.conf` holds a **cluster-admin** certificate. Treat it like a root password: never commit it, never share it.

Now ask the cluster about itself:

<!-- test: on=k8s-cp; contains=NotReady; output -->
```bash
kubectl get nodes
```

```text
NAME     STATUS     ROLES           AGE   VERSION
k8s-cp   NotReady   control-plane   4s    v1.37.1
```

**`NotReady` is expected here.** Let's see why instead of guessing:

<!-- test: on=k8s-cp; contains=NetworkPluginNotReady; output=tail:3 -->
```bash
kubectl describe node k8s-cp | grep -E 'Ready|NetworkReady|network plugin' | head -5
```

```text
  Ready            False   Sun, 04 Oct 2026 14:46:14 +0000   Sun, 04 Oct 2026 14:46:08 +0000   KubeletNotReady              container runtime network not ready: NetworkReady=false reason:NetworkPluginNotReady message:Network plugin returns error: cni plugin not initialized
```

Read the message: `NetworkReady=false reason:NetworkPluginNotReady ... cni plugin not initialized`. The container runtime
has **no pod network** yet, so the kubelet reports the node as not ready. CoreDNS (installed by `kubeadm init` a few seconds
after the control plane) waits for the same reason:

<!-- test: on=k8s-cp; retry=30; contains=coredns; contains=kube-proxy; output -->
```bash
kubectl get pods -n kube-system
```

```text
NAME                             READY   STATUS    RESTARTS   AGE
coredns-559f6c778d-94jqc         0/1     Pending   0          1s
coredns-559f6c778d-gpbqb         0/1     Pending   0          1s
etcd-k8s-cp                      1/1     Running   0          7s
kube-apiserver-k8s-cp            0/1     Running   0          7s
kube-controller-manager-k8s-cp   0/1     Running   0          7s
kube-proxy-9kw2g                 1/1     Running   0          2s
kube-scheduler-k8s-cp            1/1     Running   0          8s
```

The control-plane Pods (`etcd-k8s-cp`, `kube-apiserver-k8s-cp`, ...) run on the host network and are `Running`. The
two `coredns` Pods are `Pending`: they need a pod network.

## Step 6 · Install the pod network: Flannel (🖥️ on k8s-cp)

Kubernetes requires that every Pod can reach every other Pod by its IP address, on any node, without NAT. Kubernetes
itself does not implement that: a **CNI plugin** (Container Network Interface) does. Flannel is one of the simplest:
it gives each node a /24 out of `10.244.0.0/16` and tunnels traffic between nodes over VXLAN (UDP 8472).

```text
  Pod 10.244.1.5 (k8s-worker) ──► flannel.1 ──VXLAN over the VM network──► flannel.1 ──► Pod 10.244.0.4 (k8s-cp)
```

<!-- test: on=k8s-cp; contains=daemonset.apps/kube-flannel-ds created -->
```bash
kubectl apply -f https://github.com/flannel-io/flannel/releases/download/v0.28.9/kube-flannel.yml
```

Let's verify before moving forward. The node becomes `Ready` within a minute:

<!-- test: on=k8s-cp; retry=60; contains=Ready; absent=NotReady; output -->
```bash
kubectl wait --for=condition=Ready node/k8s-cp --timeout=10s
kubectl get nodes
```

```text
node/k8s-cp condition met
NAME     STATUS   ROLES           AGE   VERSION
k8s-cp   Ready    control-plane   17s   v1.37.1
```

<!-- test: on=k8s-cp; retry=60; absent=Pending; absent=ContainerCreating; output -->
```bash
kubectl get pods -A
```

```text
NAMESPACE      NAME                             READY   STATUS    RESTARTS   AGE
kube-flannel   kube-flannel-ds-42g26            1/1     Running   0          22s
kube-system    coredns-559f6c778d-94jqc         1/1     Running   0          24s
kube-system    coredns-559f6c778d-gpbqb         1/1     Running   0          24s
kube-system    etcd-k8s-cp                      1/1     Running   0          30s
kube-system    kube-apiserver-k8s-cp            1/1     Running   0          30s
kube-system    kube-controller-manager-k8s-cp   1/1     Running   0          30s
kube-system    kube-proxy-9kw2g                 1/1     Running   0          25s
kube-system    kube-scheduler-k8s-cp            1/1     Running   0          31s
```

Flannel runs as a DaemonSet (one Pod per node) in the `kube-flannel` namespace, and CoreDNS is `Running` now.

## Step 7 · Add the worker: `kubeadm join` (🖥️ on k8s-worker)

To join, the worker needs three things: the **API server address**, a **bootstrap token** (proves the worker may join)
and the **CA certificate hash** (proves to the worker that it is talking to the real control plane, not an impostor).
The control plane prints a ready-made command:

<!-- test: on=k8s-cp; contains=kubeadm join; contains=--discovery-token-ca-cert-hash sha256: -->
```bash
sudo kubeadm token create --print-join-command
```

Copy that line, open a shell on the worker (`multipass shell k8s-worker`) and run it there with `sudo` in front:

<!-- test: skip -->
```bash
sudo kubeadm join 10.0.0.10:6443 --token abcdef.0123456789abcdef --discovery-token-ca-cert-hash sha256:<hash>
```

Or do the copy and paste from your computer in one go, letting Multipass carry the command across:

<!-- test: timeout=600; contains=This node has joined the cluster; output=tail:6 -->
```bash
JOIN=$(multipass exec k8s-cp -- sudo kubeadm token create --print-join-command)
multipass exec k8s-worker -- sudo $JOIN
```

```text
...

This node has joined the cluster:
* Certificate signing request was sent to apiserver and a response was received.
* The Kubelet was informed of the new secure connection details.

Run 'kubectl get nodes' on the control-plane to see this node join the cluster.
```

The worker's kubelet received a certificate and now reports to the API server. Back on the control plane:

<!-- test: on=k8s-cp; retry=90; contains=k8s-worker; absent=NotReady; output -->
```bash
kubectl wait --for=condition=Ready node/k8s-worker --timeout=10s
kubectl get nodes -o wide
```

```text
node/k8s-worker condition met
NAME         STATUS   ROLES           AGE   VERSION   INTERNAL-IP   EXTERNAL-IP   OS-IMAGE             KERNEL-VERSION              CONTAINER-RUNTIME
k8s-cp       Ready    control-plane   46s   v1.37.1   10.97.7.168   <none>        Ubuntu 24.04.5 LTS   6.8.0-142-generic (amd64)   containerd://2.3.6
k8s-worker   Ready    <none>          10s   v1.37.1   10.97.7.171   <none>        Ubuntu 24.04.5 LTS   6.8.0-142-generic (amd64)   containerd://2.3.6
```

Two nodes, both `Ready`. The `ROLES` column shows `<none>` for the worker; that column only reflects a label. Adding it
is cosmetic, but makes `kubectl get nodes` easier to read:

<!-- test: on=k8s-cp; contains=labeled -->
```bash
kubectl label node k8s-worker node-role.kubernetes.io/worker=
```

## Step 8 · Verify the cluster (🖥️ on k8s-cp)

The same checklist runs after every installation method in this repository ([docs/11](../docs/11-cluster-verification.md)).

<!-- test: on=k8s-cp; contains=is running at; output -->
```bash
kubectl cluster-info
```

```text
Kubernetes control plane is running at https://10.97.7.168:6443
CoreDNS is running at https://10.97.7.168:6443/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy

To further debug and diagnose cluster problems, use 'kubectl cluster-info dump'.
```

<!-- test: on=k8s-cp; contains=kube-system; contains=kube-flannel; output -->
```bash
kubectl get namespaces
```

```text
NAME              STATUS   AGE
default           Active   47s
kube-flannel      Active   36s
kube-node-lease   Active   47s
kube-public       Active   47s
kube-system       Active   47s
```

The control-plane components report their own health on the API server's `/readyz` endpoint:

<!-- test: on=k8s-cp; contains=readyz check passed; output=tail:4 -->
```bash
kubectl get --raw='/readyz?verbose'
```

```text
...
[+]poststarthook/apiservice-openapi-controller ok
[+]poststarthook/apiservice-openapiv3-controller ok
[+]shutdown ok
readyz check passed
```

### A small test workload

Two nginx Pods, a NodePort Service in front of them, and a request through it:

<!-- test: on=k8s-cp; contains=deployment.apps/web created -->
```bash
kubectl create deployment web --image=nginx:1.30-alpine --replicas=2
kubectl expose deployment web --port=80 --type=NodePort
```

<!-- test: on=k8s-cp; retry=60; contains=2/2; output -->
```bash
kubectl rollout status deployment/web --timeout=10s
kubectl get deployment web
kubectl get pods -l app=web -o wide
```

```text
Waiting for deployment "web" rollout to finish: 0 of 2 updated replicas are available...
Waiting for deployment "web" rollout to finish: 1 of 2 updated replicas are available...
deployment "web" successfully rolled out
NAME   READY   UP-TO-DATE   AVAILABLE   AGE
web    2/2     2            2           5s
NAME                   READY   STATUS    RESTARTS   AGE   IP           NODE         NOMINATED NODE   READINESS GATES
web-6f5d6d9c94-2zks8   1/1     Running   0          5s    10.244.1.3   k8s-worker   <none>           <none>
web-6f5d6d9c94-fl5c7   1/1     Running   0          5s    10.244.1.2   k8s-worker   <none>           <none>
```

Both Pods run on `k8s-worker`: the control plane has a **taint** that keeps ordinary workloads away from it. Now call the
Service through the worker's IP address and the NodePort Kubernetes picked (30000-32767):

<!-- test: on=k8s-cp; retry=30; contains=Welcome to nginx; output -->
```bash
NODE_PORT=$(kubectl get service web -o jsonpath='{.spec.ports[0].nodePort}')
WORKER_IP=$(kubectl get node k8s-worker -o jsonpath='{.status.addresses[?(@.type=="InternalIP")].address}')
echo "http://$WORKER_IP:$NODE_PORT"
curl -s "http://$WORKER_IP:$NODE_PORT" | grep -o '<title>.*</title>'
```

```text
http://10.97.7.171:30883
<title>Welcome to nginx!</title>
```

And one more check that is easy to forget: **cross-node Pod networking**. From the control plane, reach a Pod's IP
address directly. That traffic goes through Flannel's VXLAN tunnel to the worker:

<!-- test: on=k8s-cp; retry=20; contains=Welcome to nginx; output -->
```bash
POD_IP=$(kubectl get pods -l app=web -o jsonpath='{.items[0].status.podIP}')
echo "Pod IP: $POD_IP"
curl -s --max-time 5 "http://$POD_IP" | grep -o '<title>.*</title>'
```

```text
Pod IP: 10.244.1.3
<title>Welcome to nginx!</title>
```

**The cluster works:** both nodes Ready, system Pods running, a Deployment scheduled, a Service reachable, and Pods
reachable across nodes.

## Step 9 · Use the cluster from your own computer (optional)

You normally manage a cluster from your laptop, not from inside a node. Copy the kubeconfig out (it holds the admin
certificate: keep it private):

<!-- test: contains=k8s-cp; contains=k8s-worker -->
```bash
multipass exec k8s-cp -- cat /home/ubuntu/.kube/config > kubeconfig-lab
kubectl --kubeconfig kubeconfig-lab get nodes
```

`--kubeconfig` (or the `KUBECONFIG` environment variable) chooses the file; without it, kubectl reads `~/.kube/config`.

<!-- test-run: rm -f kubeconfig-lab -->

## Common errors

| Symptom | Usual cause | Where to look |
|---|---|---|
| `kubeadm init` stops at preflight with `container runtime is not running` | containerd not configured for CRI | [troubleshooting/03](../troubleshooting/03-kubeadm-init-failure.md) |
| nodes stay `NotReady` | no CNI yet, or the kubelet/runtime stopped | [troubleshooting/01](../troubleshooting/01-node-not-ready.md) |
| `The connection to the server localhost:8080 was refused` | kubectl has no kubeconfig | [troubleshooting/05](../troubleshooting/05-kubectl-connection.md) |
| `kubeadm join` hangs or fails | wrong token, firewall, API server not reachable | [troubleshooting/04](../troubleshooting/04-worker-join-failure.md) |
| Pods run, but cannot reach Pods on the other node | IP forwarding or the CNI | [troubleshooting/02](../troubleshooting/02-pod-networking.md) |

## Cleanup

Keep the cluster for the [troubleshooting labs](../troubleshooting/README.md), then remove it with
[kubeadm/cleanup.md](cleanup.md).

## Practical challenge

[labs/01-kubeadm-installation.md](../labs/01-kubeadm-installation.md): add a **second worker** to this cluster on your
own, using only what you learned here.

## Real-world usage

You will meet kubeadm-built clusters in companies that run Kubernetes themselves: on-premises data centres, bare metal,
private clouds, edge sites, and in Kubernetes administration work (upgrades, certificate renewal, adding nodes). Even if
you only ever use managed Kubernetes, knowing what kubeadm sets up is what lets you debug a cluster instead of guessing.

## Key takeaways

- You prepare the machines (swap, kernel modules, sysctl, runtime); kubeadm builds Kubernetes on top.
- The control plane is four programs started by the kubelet from static Pod manifests in `/etc/kubernetes/manifests`.
- Nodes are `NotReady` until a CNI plugin provides the pod network.
- Joining needs the API server address, a token and the CA hash: `kubeadm token create --print-join-command`.
- Always verify: nodes, system Pods, a workload, a Service, and cross-node Pod traffic.

Next: [docs/06 · CNI networking](../docs/06-cni-networking.md) · then the [troubleshooting labs](../troubleshooting/README.md)
