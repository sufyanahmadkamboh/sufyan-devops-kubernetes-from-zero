# 07 · MicroK8s

> Goal: install Kubernetes as a single package, understand what is different inside, and publish the app on port 80
> through an Ingress. Time: about 60 minutes. Level 7 of the [roadmap](../README.md#4-the-roadmap).

## Before you start

Multipass works and you have about 4 GB of free memory for one more VM (`k8s-micro`).

## The walk

### 1. Read docs/09 · How MicroK8s works inside

Open [docs/09](../docs/09-microk8s-internals.md). Three ideas to keep:

- **One snap package.** `snap install` brings Kubernetes, containerd and the tools, confined and versioned by
  **channel** (`1.36/stable`). Pinning the channel means you decide when to move to the next minor version.
- **kubelite.** The API server, scheduler, controller manager, kubelet and proxy run in **one process**, not as Pods.
- **dqlite instead of etcd**, and **Calico** as the default CNI.

```text
 k8s-micro (Ubuntu VM)
 └── snap "microk8s"
     ├── kubelite      (API server, scheduler, controller manager, kubelet, kube-proxy in one process)
     ├── k8s-dqlite    (the datastore)
     ├── containerd
     └── Pods: Calico, CoreDNS, your apps
```

### 2. The lesson, Steps 1–7

Open [microk8s/README.md](../microk8s/README.md) and run **Steps 1–7** inside `k8s-micro`.

What to watch for:

- **Step 2, the group.** MicroK8s commands need root or membership in the `microk8s` group, and group membership only
  applies to **new** login sessions. If you get `Insufficient permissions to access MicroK8s`, log out and back in.
  This trips up almost everyone once.
- **Step 3.** `microk8s status --wait-ready` ends with `microk8s is running` and lists the add-ons.
- **Step 4.** `kubectl get pods -A` shows **no** `kube-apiserver` or `etcd` Pods. Compare that with chapter 03. They
  are inside `kubelite`, which you see in the list of `snap.microk8s.*` systemd units instead.
- **Step 4, the alias.** `snap alias microk8s.kubectl kubectl` makes plain `kubectl` use MicroK8s's bundled client. If
  you already have another kubectl on that machine, keep the `microk8s` prefix instead.
- **Step 7.** `microk8s inspect` packs services, network settings and logs into one report: the first thing to attach
  to a bug report or send to a colleague.

### 3. Lab 03 · Publish the app through an Ingress

Do [labs/03](../labs/03-microk8s-installation.md) before you clean up. Without opening the solution, enable the ingress
add-on and write one Ingress rule so that `web.local` on port 80 reaches the `web` Service.

The picture to understand:

```text
 curl -H 'Host: web.local' http://127.0.0.1/
        │
        ▼
 Traefik ingress controller (port 80)            ── reads ──►  Ingress "web": web.local/* → Service web:80
        │
        ▼
 Service web ──► Pod web-…  /  Pod web-…
```

An Ingress object by itself does nothing; the **controller** reads the rules and does the routing. A request for a host
name with no rule gets the controller's `404`.

### 4. Cleanup

Remove MicroK8s and the VM with [microk8s/cleanup.md](../microk8s/cleanup.md). Notice the `--purge` warning: it removes
every object and volume without keeping a snapshot.

## Expert commentary

- **Why it matters at work.** MicroK8s shows up on single machines, edge devices and small fleets (factories, shops,
  IoT gateways) where one package and automatic HA with three nodes are worth more than full control. Snaps refresh
  automatically; in production you control that (a fixed channel, refresh windows or holds).
- **Ingress at work.** The same three objects (Ingress → Service → Pods) exist on every cluster. Only the controller
  changes: Traefik here, the AWS Load Balancer Controller on EKS, and the newer Gateway API with the same idea.
- **Common mistakes.** Forgetting the new login after `usermod`; mixing two kubectl binaries; expecting `kubectl get
  pods -n kube-system` to show the control plane.
- **What an interviewer asks.** "What is the difference between a Service and an Ingress?" "Why does MicroK8s not show
  an API server Pod?" "How would you pin the Kubernetes version of a MicroK8s install?"

## Checkpoint

You are done when:

- [ ] MicroK8s ran, the test app answered on its NodePort, and you know why `kubectl` worked without a prefix
- [ ] you can explain kubelite and dqlite in one sentence each
- [ ] lab 03 is done: `web.local` answered on port 80, and an unknown host got `404`
- [ ] `k8s-micro` is deleted and `multipass list` no longer shows it

Next: [08 · Amazon EKS](08-eks.md)
