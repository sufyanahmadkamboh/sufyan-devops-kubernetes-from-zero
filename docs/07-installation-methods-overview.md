# 07 · The four installation methods

> Time: 15 minutes · An overview before the hands-on lessons. The detailed side-by-side comparison is in
> [docs/13](13-installation-comparison.md).

All four methods give you the **same Kubernetes API**: the same `kubectl` commands and the same YAML work everywhere.
They differ in who runs the control plane, where the nodes are, and how much you must do yourself.

```text
   more control, more work                                              less control, less work
   ◄─────────────────────────────────────────────────────────────────────────────────────────────►
   kubeadm                 MicroK8s                    Minikube                 Amazon EKS
   you build every layer   one snap, everything in     one command, a cluster   AWS runs the control plane,
   on real Linux machines  it, real Linux machines     in a container/VM        you run (or rent) workers
   self-managed            self-managed / edge         local only               managed, production cloud
```

## kubeadm

- **What:** the official bootstrapper. You prepare Linux machines (prerequisites, containerd, packages), then
  `kubeadm init` creates the control plane and `kubeadm join` adds nodes. You install the CNI yourself.
- **Components:** control plane as static Pods; etcd as a static Pod; kubelet and containerd as systemd services.
- **Who uses it:** platform teams running on-premises or bare metal, anyone preparing for the CKA exam, and tools
  built on top of it (Cluster API, kind, Minikube).
- **Pros:** standard, transparent, every layer visible; you learn how a cluster really works.
- **Cons:** you own everything: HA, upgrades, certificates, backups, the CNI.
- **Lesson:** [kubeadm on Ubuntu](../kubeadm/README.md) (Kubernetes v1.37, containerd 2.x, Flannel v0.28.9).

## Minikube

- **What:** a local, throw-away cluster on your computer, usually as one Docker container (the "node"), also as a VM.
- **Components:** everything inside the node container (it uses kubeadm internally); add-ons with one command.
- **Who uses it:** developers testing manifests and Helm charts, trainers, CI jobs.
- **Pros:** one command, runs on Windows, macOS and Linux, profiles for several clusters, easy reset.
- **Cons:** not for production; limited by your laptop's resources; networking differs from real clusters.
- **Lesson:** [Minikube](../minikube/README.md) (v1.39.0).

## MicroK8s

- **What:** Canonical's lightweight Kubernetes, packaged as one **snap**. Installs on any Linux with snap support,
  joins several machines into a cluster with `microk8s add-node`.
- **Components:** control plane in one process (**kubelite**), datastore **dqlite** instead of etcd, containerd and
  Calico included; add-ons with `microk8s enable`.
- **Who uses it:** edge and IoT, small self-managed clusters, developers on Ubuntu, CI.
- **Pros:** one command install, automatic security updates within a track, small footprint, HA with three nodes.
- **Cons:** snap-specific layout and commands (`microk8s kubectl`), less common in large enterprises.
- **Lesson:** [MicroK8s](../microk8s/README.md) (track `1.36/stable`, the newest stable track at the time of writing).

## Amazon EKS

- **What:** AWS's managed Kubernetes. AWS runs and scales the control plane across availability zones; you choose the
  worker nodes (managed node groups, Fargate, or EKS Auto Mode).
- **Components:** control plane and etcd invisible to you; workers are EC2 instances; Amazon VPC CNI, CoreDNS and
  kube-proxy as add-ons; IAM controls access.
- **Who uses it:** companies running production workloads on AWS.
- **Pros:** no control plane to operate, integrated with AWS (IAM, load balancers, EBS volumes), upgrades by API.
- **Cons:** costs money from the first minute (control plane per hour, nodes, NAT gateway, load balancers); AWS
  networking and IAM knowledge required; resources must be deleted carefully.
- **Lesson:** [Amazon EKS with eksctl](../eks/README.md) (EKS 1.37, eu-central-1, with a cost table and a verified
  teardown in [eks/cleanup.md](../eks/cleanup.md)).

## Which one when?

| Situation | Choose |
|---|---|
| "I want to understand how Kubernetes is put together" | kubeadm |
| "I need a cluster on my laptop in 2 minutes" | Minikube |
| "Small cluster on a few Linux boxes, or at the edge" | MicroK8s |
| "Production on AWS" | EKS |
| "Production on my own hardware" | kubeadm (with HA, automation and backups), or a distribution built on it |

## The order of this course

```text
 kubeadm (learn every layer) → troubleshooting labs 01–07 → Minikube → troubleshooting lab 08 → MicroK8s → EKS
```

kubeadm comes first on purpose: once you have built every layer yourself, the other three are easy to understand,
because you know what they are doing for you.

## Check yourself

<details><summary>1. Which methods let you see the API server as a Pod?</summary>

kubeadm and Minikube (static Pods). MicroK8s runs it inside kubelite; EKS runs it outside your account.
</details>

<details><summary>2. Which method costs money while it runs, and why does that matter?</summary>

EKS: the control plane, EC2 nodes, NAT gateway and load balancers are billed per hour, so you must delete everything
when you are done and verify it is gone.
</details>

<details><summary>3. What does MicroK8s use instead of etcd?</summary>

dqlite, a distributed SQLite.
</details>

<details><summary>4. A team wants production Kubernetes in their own data centre. Which method fits?</summary>

kubeadm with a highly available control plane, automation and backups (or a distribution that builds on it).
MicroK8s is an option for smaller clusters.
</details>

Next: [Start the hands-on lessons](../kubeadm/README.md)
