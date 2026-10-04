# 13 · Comparing the installation methods

> Time: 15 minutes · Read it after the four installation lessons, then try [lab 05](../labs/05-installation-comparison.md).

You have now installed Kubernetes four ways. They all give you the **same Kubernetes API**: the same `kubectl`
commands and the same YAML work on each. What differs is who runs the control plane, how many machines you need, and
what the result is good for.

## Side by side

| | kubeadm | Minikube | MicroK8s | Amazon EKS |
|---|---|---|---|---|
| **Purpose** | build a real cluster on machines you control | a local cluster for development and learning | a lightweight cluster for one or a few Linux machines, edge, IoT | managed production Kubernetes on AWS |
| **Setup effort** | highest: prepare every node (swap, kernel modules, runtime, packages), init, CNI, join | one command | one `snap install` | a config file + one eksctl command; AWS knowledge for networking and IAM |
| **Setup time** | the longest by hand (the lesson's two-node build is the longest lesson) | a few minutes after the first download | a few minutes | about 15 minutes for AWS to create it (14.5 min in the lesson's run) |
| **Nodes** | any number of machines | 1 (or several containers on one computer) | 1 to many machines | managed node groups, Auto Mode, Fargate |
| **High availability** | yes, if you build it: 3 control-plane nodes + a load balancer for the API, etcd quorum | no | yes, automatic from 3 nodes | yes, built in: the control plane runs in 3 availability zones |
| **Default CNI** | none, you choose (Flannel in the lesson) | built in (kindnet for multi-node; bridge for one node) | Calico | Amazon VPC CNI (Pods get VPC IPs) |
| **Datastore** | etcd (static Pod on the control plane) | etcd inside the node | dqlite | etcd run by AWS (invisible to you) |
| **Container runtime** | your choice of CRI runtime; containerd in the lesson | containerd inside the node container | containerd bundled in the snap | containerd on the EKS AMI (AL2023) |
| **Upgrades** | you: `kubeadm upgrade` node by node, plus packages | `minikube start --kubernetes-version=…` or recreate | snap refresh (patches automatic within a track; you change the track for minors) | control plane: one click/command; nodes: managed rolling update |
| **Cost** | your hardware or VMs | free (your laptop) | free (your machines) | per-hour control plane + EC2 + NAT + load balancers (lab ≈ $0.25–0.30/h) |
| **Production use** | yes: on-premises and bare metal, the base of many distributions | no | yes for edge, small and appliance-like clusters | yes, very common |
| **Learning value** | highest: you see and configure every component | fast feedback for kubectl and YAML | fast, shows a different packaging model | how real cloud teams run Kubernetes: VPC, IAM, load balancers, cost |

## Which one should I use?

```text
                         What do you need right now?
                                   │
         ┌─────────────────────────┼──────────────────────────┐
         ▼                         ▼                          ▼
  learn / develop on       run on machines you own      run production in the cloud
  my own computer          (servers, VMs, edge boxes)
         │                         │                          │
         ▼                         ▼                          ▼
  Docker installed?        need full control and          on AWS? ──▶ Amazon EKS
   yes ──▶ Minikube        standard upstream layout?      (Azure: AKS, Google Cloud: GKE)
   Linux, no Docker         yes ──▶ kubeadm
   ──▶ MicroK8s (or        small / edge / few people
       Minikube + VM        to operate it?
       driver)               ──▶ MicroK8s
```

And for **understanding how Kubernetes works** (exams, interviews, debugging): build it once with kubeadm.

## Real-world scenarios

| Scenario | Good choice | Why |
|---|---|---|
| A developer tests Helm charts and manifests on a laptop | Minikube | one command, deleted in seconds, runs next to Docker |
| A CI pipeline needs a throwaway cluster for every pull request | Minikube (or kind) on the CI runner; MicroK8s on a Linux runner | starts in minutes, no cloud cost, removed with the runner |
| Shops or factory sites each run a small cluster on two or three boxes | MicroK8s | snap updates, small footprint, HA from three nodes |
| A company runs Kubernetes in its own data center | kubeadm (or a distribution built on it) | standard upstream layout, full control over network, storage and upgrades |
| A team runs customer-facing services on AWS | Amazon EKS | no control plane to operate, integrates with VPC, IAM, load balancers, autoscaling |
| Preparing for the CKA exam | kubeadm | the exam asks you to install, upgrade, back up and troubleshoot kubeadm clusters |

## What stays the same everywhere

- The API, `kubectl`, and the YAML in [examples/nginx](../examples/nginx/README.md).
- The [verification checklist](11-cluster-verification.md): the same eight checks pass on every cluster.
- The troubleshooting method: `get` → `describe` → `logs` → node services.

## Check yourself

<details><summary>Which method gives you a highly-available control plane without any extra work?</summary>

Amazon EKS: AWS runs the control plane across three availability zones. MicroK8s also becomes HA automatically, but
only after you add three nodes.
</details>

<details><summary>You need a cluster in an air-gapped factory on three small industrial PCs. Which method fits, and why?</summary>

MicroK8s: small footprint, one package per node, automatic HA with three nodes, and snaps can be installed offline.
kubeadm also works but needs more operations effort.
</details>

<details><summary>Why is kubeadm the best way to learn, even if you will use EKS at work?</summary>

You set up every component yourself (runtime, kubelet, certificates, CNI, join), so you understand what EKS hides and
can debug the parts you still own (nodes, CNI, workloads).
</details>

<details><summary>Will a Deployment YAML written on Minikube work on EKS?</summary>

Yes, the API is the same. What usually changes is how it is exposed (LoadBalancer vs NodePort), storage classes, and
resource sizing.
</details>

Back to the roadmap: [../README.md](../README.md)
