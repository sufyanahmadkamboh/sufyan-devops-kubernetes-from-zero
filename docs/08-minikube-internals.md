# 08 · How Minikube works inside

> Time: 15 minutes · Read it before or after the [Minikube lesson](../minikube/README.md).

Minikube looks like magic: one command, and a whole Kubernetes cluster runs on your laptop. This chapter opens the box.
Everything inside is the same Kubernetes you build by hand in the [kubeadm lesson](../kubeadm/README.md), packed so it
fits in a single machine (or a single container).

## The big idea: one "node" that Minikube creates for you

A Kubernetes node is normally a whole machine. Minikube creates that machine for you, using a **driver**:

| Driver | What the node is | Typical use |
|---|---|---|
| `docker` (default when Docker is installed) | a Docker **container** | Linux, Windows and macOS with Docker Desktop / Docker Engine |
| `podman` | a Podman container | Linux without Docker (still marked experimental by Minikube) |
| `hyperv` | a Hyper-V virtual machine | Windows Pro/Enterprise without Docker |
| `kvm2` | a KVM virtual machine | Linux, when you want a real VM |
| `qemu` | a QEMU virtual machine | macOS on Apple silicon, Linux |
| `none` / `ssh` | your own machine, or a remote one | special cases; not for learning |

In this course we use `--driver=docker`. Then the "node" is a container named `minikube`, and **inside** that
container run systemd, containerd, the kubelet, and the control plane:

```text
 Your computer
 └── Docker Engine
     └── container "minikube"  (image: kicbase, the "Kubernetes in container" base image)
         ├── systemd                         starts the services below, like on a real Linux machine
         ├── containerd                      the container runtime (CRI) for the cluster
         ├── kubelet                         the node agent
         └── containers started by containerd, inside the minikube container:
             ├── kube-apiserver, etcd, kube-scheduler, kube-controller-manager   (static Pods)
             ├── kube-proxy, CoreDNS
             ├── storage-provisioner        (Minikube's own: creates volumes for PersistentVolumeClaims)
             └── your Pods (web, ...)
```

So there are **containers inside a container**. That is why, in the lesson, `docker ps` shows only one container,
`minikube`, while `minikube ssh -- sudo crictl ps` shows all the Kubernetes components.

## What `minikube start` does

```text
 1. Pick the driver and check resources      (CPUs, memory, free disk; refuses below the minimum)
 2. Download the kicbase image + a preloaded  (a tarball with all Kubernetes images, so the start is fast)
    image bundle for the Kubernetes version
 3. Create the node                          (docker run ... kicbase)
 4. Run kubeadm INSIDE the node              (yes: Minikube uses kubeadm to build the control plane)
 5. Install a CNI if needed, CoreDNS, the storage provisioner
 6. Write a context "minikube" into ~/.kube/config and make it the current context
```

Step 4 is worth remembering: the certificates, static Pod manifests and `/etc/kubernetes` layout inside the node are
the same as on a kubeadm cluster. What you learn in one applies to the other.

## Where things live

| What | Where |
|---|---|
| Minikube's own files (cached images, profiles, certificates, logs) | `~/.minikube` |
| The kubeconfig entry (context and cluster named after the profile) | `~/.kube/config` |
| The node | the Docker container `minikube` (or one container per node: `multinode`, `multinode-m02`, ...) |
| Inside the node: Kubernetes configuration | `/etc/kubernetes` (open it with `minikube ssh`) |

## Profiles: several clusters side by side

A **profile** is one complete cluster with its own name. The default profile is called `minikube`. In the lesson you
create a second one:

```text
minikube start -p multinode --nodes 2 --driver=docker --cpus=2 --memory=2200
kubectl --context multinode get nodes
minikube profile list
minikube delete -p multinode
```

Every `minikube` command takes `-p <profile>`. Every profile is also a kubectl **context**, so you switch with
`kubectl config use-context <name>` or `--context`.

## Multi-node

`--nodes 2` creates a second container (`multinode-m02`) and joins it as a worker, again with kubeadm. Minikube
installs a CNI (kindnet) so Pods on the two nodes can reach each other. It is good for seeing scheduling across
nodes and DaemonSets. It is **not** high availability: both "nodes" share your one computer.

## Add-ons

Add-ons are optional components Minikube installs with one command: `metrics-server`, `dashboard`, `ingress`,
`registry` and many more. `minikube addons list` shows them; `minikube addons enable metrics-server` installs one.
They are ordinary Kubernetes objects; `kubectl get pods -n kube-system` shows them afterwards.

## Reaching your Services: `minikube service` and `minikube tunnel`

With the Docker driver on Windows and macOS, the node's IP lives inside Docker's own network and is not reachable from
your computer. Minikube solves this in two ways:

| Command | What it does | Use it for |
|---|---|---|
| `minikube service web --url` | prints a URL (and on Windows/macOS keeps a port-forward open while it runs) | NodePort Services; used in the lesson |
| `minikube tunnel` | runs a route/proxy so `LoadBalancer` Services get an external IP | testing `type: LoadBalancer` locally |

On Linux with the Docker driver, `minikube ip` + the NodePort also works directly.

## How big should it be?

| Setting | Minimum | Comfortable for this course |
|---|---|---|
| CPUs | 2 | 2 |
| Memory | about 1.8 GB (Minikube refuses less, see [troubleshooting 08](../troubleshooting/08-insufficient-resources.md)) | 4096 MB (`--memory=4096`) |
| Disk | about 20 GB free | 20 GB+ |

The memory goes to the node container and is shared by the control plane, system Pods and your workloads.

## Check yourself

<details><summary>With the Docker driver, how many Docker containers does a one-node Minikube cluster create, and where do the Kubernetes components run?</summary>

One container, `minikube`. The components run as containers **inside** it, started by the containerd that runs inside
the node container. `docker ps` on your computer only shows the node.
</details>

<details><summary>Which tool does Minikube use internally to build the control plane?</summary>

kubeadm. That is why the layout inside the node (`/etc/kubernetes`, static Pods, certificates) matches the kubeadm lesson.
</details>

<details><summary>What is a profile, and how do you talk to a second profile with kubectl?</summary>

A complete, separately named cluster. Each profile is also a kubectl context of the same name:
`kubectl --context multinode get nodes`, or `kubectl config use-context multinode`.
</details>

<details><summary>Your NodePort Service works inside the cluster, but the node IP is not reachable from your Windows laptop. Why, and what do you use?</summary>

With the Docker driver on Windows/macOS the node lives in Docker's internal network. Use `minikube service web --url`
(or `minikube tunnel` for LoadBalancer Services).
</details>

<details><summary>Is a two-node Minikube cluster highly available?</summary>

No. Both nodes are containers on the same computer, and there is one control plane. It is useful to learn scheduling
across nodes, not for availability.
</details>

Next: [09 · How MicroK8s works inside](09-microk8s-internals.md)
