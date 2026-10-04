# 03 · Control plane and CNI

> Goal: a running control plane, a node that turns from `NotReady` to `Ready`, and you know why.
> Time: about 45 minutes. Level 3 of the [roadmap](../README.md#4-the-roadmap).

## Before you start

Both machines passed the [chapter 02 checkpoint](02-prepare-the-machines.md#checkpoint). Everything in this chapter
runs on **k8s-cp** only.

## The walk

### 1. Read docs/05 · What kubeadm does, step by step

Open [docs/05](../docs/05-kubeadm-installation.md) and read the phases of `kubeadm init`. Keep this picture in mind
while the command runs; it prints one line per phase:

```text
 preflight ─► certs ─► kubeconfig ─► kubelet-start ─► control-plane + etcd (static Pods)
          ─► wait for API server ─► upload-config ─► mark-control-plane ─► bootstrap-token ─► addons (CoreDNS, kube-proxy)
```

### 2. Step 5 of the lesson: `kubeadm init`

Run **Step 5** of [kubeadm/README.md](../kubeadm/README.md) on k8s-cp.

Watch the output scroll by and look for the phase names in square brackets: `[preflight]`, `[certs]`,
`[kubeconfig]`, `[control-plane]`, `[etcd]`, `[addons]`. The last lines tell you what to do next: copy the kubeconfig,
install a Pod network, join workers. **Read them.** kubeadm literally prints your next three steps.

If preflight prints `[ERROR ...]` lines, stop. kubeadm has not changed anything yet, so fix the cause and run it again.
The usual cause on these machines is the container runtime: see
[troubleshooting 03](../troubleshooting/03-kubeadm-init-failure.md).

### 3. The kubeconfig

The lesson copies `/etc/kubernetes/admin.conf` to `~/.kube/config`. That file holds a **cluster-admin certificate**.
Treat it like a root password: never commit it, never paste it into a chat, never mail it.

### 4. The NotReady moment

`kubectl get nodes` shows `k8s-cp` as `NotReady`. This is the most instructive moment of the whole lab, so don't rush
past it. The lesson asks the node why, and the real answer from our test runs is:

```text
container runtime network not ready: NetworkReady=false reason:NetworkPluginNotReady message:Network plugin returns error: cni plugin not initialized
```

Read it from the right: the CNI plugin is not initialised → the network is not ready → the kubelet reports the node as
not ready. Nothing is broken. Kubernetes simply does not ship a Pod network; you have to install one. The two CoreDNS
Pods stay `Pending` for the same reason, while the control-plane Pods (etcd, API server, scheduler, controller manager)
run, because they use the host's network.

### 5. Read docs/06 · CNI and Pod networking, then Step 6: Flannel

Open [docs/06](../docs/06-cni-networking.md). Then run **Step 6** of the lesson: one `kubectl apply` of Flannel's
manifest, and a `kubectl wait` until the node is `Ready`.

Watch for:

- `daemonset.apps/kube-flannel-ds created`: Flannel runs as a DaemonSet, one Pod per node, in the `kube-flannel`
  namespace
- the node switching to `Ready` within about a minute
- `kubectl get pods -A` with no `Pending` or `ContainerCreating` left: CoreDNS is now `Running`

> **Why `--pod-network-cidr=10.244.0.0/16`?** That is the range Flannel's default manifest expects. If you pass a
> different range to kubeadm, you must change Flannel's config to match. Mismatches give Pods IPs that nothing routes.

## Expert commentary

- **Why it matters at work.** "The node is NotReady" is the most common Kubernetes alert. The reflex to build here:
  never guess, run `kubectl describe node` and read the `Ready` condition's message. It names the component.
- **Static Pods.** The control plane runs from YAML files in `/etc/kubernetes/manifests`, started by the kubelet
  directly, not by the API server. That is how a cluster can start its own API server. If you edit those files, the
  kubelet restarts the component: powerful, and a classic way to break a cluster.
- **Common mistakes.** Running `kubectl` as root without a kubeconfig (`localhost:8080` errors: lab 05); installing a
  second CNI on top of the first; changing the Pod CIDR after `init`.
- **What an interviewer asks.** "Why are nodes NotReady after `kubeadm init`?" "What is a static Pod?" "Name three CNI
  plugins and one difference between them." "Where does kubeadm put the certificates?"

## Checkpoint

You are done when:

- [ ] `kubectl get nodes` on k8s-cp shows `k8s-cp` as `Ready`
- [ ] `kubectl get pods -A` shows etcd, kube-apiserver, kube-scheduler, kube-controller-manager, kube-proxy, CoreDNS
      and Flannel all `Running`
- [ ] you can explain the NotReady message word by word
- [ ] you know where `admin.conf`, the certificates (`/etc/kubernetes/pki`) and the static Pod manifests live

Next: [04 · Workers and verification](04-workers-and-verification.md)
