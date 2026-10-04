# 01 · Concepts

> Goal: know what you are about to install, piece by piece, before you install it. Time: about 60 minutes.
> Level 1 of the [roadmap](../README.md#4-the-roadmap).

## Before you start

Nothing to run in this chapter. You need a notebook and about an hour of attention.

## The walk

### 1. Read docs/01 · What is Kubernetes?

Open [docs/01](../docs/01-what-is-kubernetes.md). While you read, keep one idea in mind: **Kubernetes is a loop.** You
write down the state you want ("two nginx Pods, reachable on port 80"), and controllers keep comparing that with
reality and fixing the difference. Self-healing, scaling and rolling updates are all the same loop.

```text
   desired state (what you applied)
          │
          ▼
   ┌─────────────┐   differs?   ┌───────────────────────┐
   │ controllers │ ───────────► │ create / delete / move│
   └─────────────┘              └───────────────────────┘
          ▲                                 │
          └──────── actual state ◄──────────┘
```

### 2. Read docs/02 · Kubernetes architecture

Open [docs/02](../docs/02-kubernetes-architecture.md). This is the most important doc in the repository. Every later
chapter refers back to it. Draw the diagram yourself, on paper, from memory, after reading:

- **Control plane:** kube-apiserver (the only door), etcd (the memory), kube-scheduler (picks a node),
  kube-controller-manager (runs the loops), and on clouds the cloud-controller-manager.
- **Every node:** kubelet (the node's agent), kube-proxy (Service rules), a container runtime (containerd).
- **Add-ons:** CoreDNS (names), a CNI plugin (the Pod network).

Then follow the section on what happens when you run `kubectl apply`. If you can retell that path in your own words
(kubectl → API server → etcd → controller → scheduler → kubelet → containerd → runc), you understand Kubernetes better
than many people who use it daily.

### 3. Read docs/07 · The four installation methods

Open [docs/07](../docs/07-installation-methods-overview.md). The same components exist in every cluster; the
installation methods differ in **where** they run and **who** runs them:

| | Control plane runs as | Who operates it |
|---|---|---|
| kubeadm | static Pods on your control-plane VM | you |
| Minikube | inside one Docker container on your laptop | you (but it is disposable) |
| MicroK8s | one process (`kubelite`) from a snap | you |
| EKS | in an AWS-owned account, invisible to you | AWS |

## Expert commentary

- **Why it matters at work.** When a cluster misbehaves, the question is always "which component is responsible for
  this?" The architecture diagram is your map for every incident in chapter 05.
- **Common mistake.** Thinking the API server "runs" containers. It doesn't: it only stores and serves objects. The
  kubelet on each node does the work, through the runtime.
- **What an interviewer asks.** "What happens when you run `kubectl apply -f deployment.yaml`?" and "What is etcd and
  why do you back it up?" Both are answered in docs/02.

## Checkpoint

You are done when you can, without looking:

- [ ] draw the control plane and a worker node with all their components
- [ ] explain what the scheduler decides and what the kubelet does
- [ ] explain why a cluster needs a CNI plugin and CoreDNS
- [ ] say where the control plane runs for each of the four installation methods
- [ ] answer the "Check yourself" questions at the end of docs/01, 02 and 07

Next: [02 · Prepare the machines](02-prepare-the-machines.md)
