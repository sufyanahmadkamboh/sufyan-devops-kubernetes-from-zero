# ☸️ Kubernetes From Zero · Installation & Cluster Setup, Hands-On

[![test-lessons](https://github.com/sufyanahmadkamboh/sufyan-devops-kubernetes-from-zero/actions/workflows/test.yaml/badge.svg)](https://github.com/sufyanahmadkamboh/sufyan-devops-kubernetes-from-zero/actions/workflows/test.yaml)

Install Kubernetes **four ways**, understand what each installation does, break the clusters on purpose and fix them.

| Method | What you build | Where it runs |
|---|---|---|
| [kubeadm](kubeadm/README.md) | a real two-node cluster (1 control plane + 1 worker) on Ubuntu 24.04, built by hand | two virtual machines |
| [Minikube](minikube/README.md) | a complete cluster in one container, for development | your computer |
| [MicroK8s](microk8s/README.md) | a lightweight cluster installed as one snap package | one Ubuntu machine |
| [Amazon EKS](eks/README.md) | a managed cluster on AWS, with cost control and a verified teardown | AWS (eu-central-1) |

```text
Install  ->  Verify  ->  Deploy a test app  ->  Break  ->  Troubleshoot  ->  Fix  ->  Clean up  ->  Compare
```

**Every command is tested.** The kubeadm, Minikube and MicroK8s lessons and the troubleshooting labs run end to end
on fresh virtual machines in GitHub Actions on every change ([tests/](tests/README.md)); the outputs you see in the
lessons are the real outputs of those runs. The EKS lesson was run against a real AWS account, recorded, and torn down.

## 1. Who it is for

You know basic Linux (`cd`, `ls`, `sudo`, editing a file) and what a container is. You have **never** installed
Kubernetes. No Kubernetes experience needed: [docs/01](docs/01-what-is-kubernetes.md) starts at "why does it exist".

## 2. What you will learn

- What Kubernetes is made of (control plane, nodes, add-ons) and how the pieces talk to each other
- The Linux prerequisites (swap, kernel modules, sysctls, cgroups, ports) and **why** each one is needed
- Container runtimes and the CRI: containerd 2.x, the systemd cgroup driver, `crictl`
- `kubeadm init` and `kubeadm join`, phase by phase; kubeconfig files and contexts
- Pod networking and CNI plugins (Flannel; the Amazon VPC CNI on EKS)
- Minikube profiles, drivers and add-ons; MicroK8s snaps, channels and add-ons
- Amazon EKS: managed control plane, node groups, IAM and access entries, VPC design, **costs and teardown**
- A **verification checklist** that works on every cluster, and a test workload
- **Troubleshooting**: NotReady nodes, Pod networking, failed init/join, kubectl connection errors, crashing system
  Pods, a dead container runtime, insufficient resources
- Cleaning up safely, and choosing the right installation method for a situation

**Start here:** the guided [tutorial](tutorial/README.md) walks you through the levels below in order. To read offline:
the [study guide PDF](study/study-guide.pdf), with the [glossary](study/glossary.md) and
[25 interview questions](study/interview-questions.md).

## 3. Prerequisites

| You need | For | Check it with |
|---|---|---|
| A computer with 4 CPU cores, 16 GB RAM, 40 GB free disk | kubeadm (two VMs) | |
| [Multipass](https://canonical.com/multipass) (Windows, macOS, Linux) | the Ubuntu VMs for kubeadm and MicroK8s | `multipass version` |
| Docker Desktop or Docker Engine | Minikube | `docker version` |
| Git and a terminal | everything | `git --version` |
| An AWS account **you are allowed to spend money on** (optional) | the EKS lesson, about $0.25–0.30 per hour | `aws sts get-caller-identity` |

Everything except EKS is free and runs on your computer.

## 4. The roadmap

Ten levels. Each one ends with something you can show: a working cluster, a fixed failure or a decision you can defend.

```text
 Level  1  Concepts ───────────────┐
 Level  2  Linux + runtime         │ understand
 Level  3  kubeadm control plane   ┤
 Level  4  Workers + verification  │ build by hand
 Level  5  Troubleshooting         ┤ break and fix
 Level  6  Minikube                │
 Level  7  MicroK8s                │ other ways to install
 Level  8  Amazon EKS              ┤
 Level  9  Cleanup and reset       │ operate responsibly
 Level 10  Compare + capstone ─────┘ decide and prove it
```

| Level | Goal | Read | Do | Done when |
|---|---|---|---|---|
| 1 | Know what you are installing | [docs/01](docs/01-what-is-kubernetes.md), [docs/02](docs/02-kubernetes-architecture.md) | the "Check yourself" questions | you can draw the control plane and a node from memory |
| 2 | Prepare Linux machines correctly | [docs/03](docs/03-installation-prerequisites.md), [docs/04](docs/04-container-runtime-and-cri.md) | [kubeadm](kubeadm/README.md) Steps 1–4 | both VMs have containerd answering `crictl` and kubeadm v1.37 held |
| 3 | Create a control plane | [docs/05](docs/05-kubeadm-installation.md), [docs/06](docs/06-cni-networking.md) | kubeadm Steps 5–6 | the control plane is `Ready` after Flannel |
| 4 | Add a worker and verify the cluster | [docs/07](docs/07-installation-methods-overview.md), [docs/11](docs/11-cluster-verification.md) | kubeadm Steps 7–9, [lab 01](labs/01-kubeadm-installation.md) | the test app answers through a NodePort; pods talk across nodes |
| 5 | Debug a broken cluster | [troubleshooting/](troubleshooting/README.md) | labs 01–07 | you found each root cause from the symptoms, before reading it |
| 6 | Run Kubernetes on a laptop | [docs/08](docs/08-minikube-internals.md) | [Minikube](minikube/README.md), [troubleshooting 08](troubleshooting/08-insufficient-resources.md), [lab 02](labs/02-minikube-installation.md), [examples/nginx](examples/nginx/README.md) | two profiles, two versions, and you know which one kubectl uses |
| 7 | Install with one package | [docs/09](docs/09-microk8s-internals.md) | [MicroK8s](microk8s/README.md), [lab 03](labs/03-microk8s-installation.md) | the app answers on port 80 through an Ingress |
| 8 | Run a managed cluster in the cloud | [docs/10](docs/10-eks-architecture.md) | [EKS](eks/README.md) (optional, costs money), [lab 04](labs/04-eks-installation.md) | the app answers through an AWS load balancer, then everything is deleted |
| 9 | Clean up without leftovers | [docs/12](docs/12-cleanup-and-reset.md) | [kubeadm](kubeadm/cleanup.md), [Minikube](minikube/cleanup.md), [MicroK8s](microk8s/cleanup.md), [EKS](eks/cleanup.md) cleanup | the verify step of each cleanup passes |
| 10 | Choose and justify | [docs/13](docs/13-installation-comparison.md) | [lab 05](labs/05-installation-comparison.md), [capstone](capstone/README.md) | you answered the capstone without looking things up |

Suggested order: Levels 1 → 5 in one go (the kubeadm cluster is used by all troubleshooting labs), then 6, 7, 8 in any
order, then 9 and 10.

## 5. Repository structure

```text
.
├── docs/              13 concept lessons (what, why, how; diagrams; "check yourself")
├── kubeadm/           the two-node cluster lesson, cleanup, scripts/prepare-node.sh
├── minikube/          the Minikube lesson and cleanup
├── microk8s/          the MicroK8s lesson and cleanup
├── eks/               the EKS lesson, cluster.yaml, cleanup, scripts (inventory, verify-cleanup), console screenshots
├── troubleshooting/   8 labs: break it, investigate, fix, verify
├── labs/              5 practical challenges with hidden solutions
├── examples/nginx/    the test workload as YAML (Deployment, NodePort and LoadBalancer Services)
├── capstone/          the final questions and scenario
├── tutorial/          the guided course: a senior engineer walks you through the repository, chapter by chapter
├── study/             glossary, 25 interview questions, and the printable study guide (PDF)
├── video/             the video course (18 chapters), built from the recorded runs
└── tests/             the runner that executes every lesson (mdrun.py) and the CI helpers
```

## 6. How every installation lesson is written

All four installation lessons follow the same 15 points, so you always know where to look:

1. What is it? · 2. Why does it exist? · 3. When should I use it? · 4. What do I need before starting? · 5. What are we
building (diagram)? · 6. Step-by-step installation · 7. What happens during installation · 8. Verification ·
9. Expected output (real) · 10. Common errors · 11. Troubleshooting · 12. Cleanup · 13. Practical challenge ·
14. Real-world usage · 15. Key takeaways

Commands that delete something are always announced like this:

```text
⚠️ DESTRUCTIVE COMMAND · what it deletes
```

## 7. Versions used (checked against the official sources)

| Component | Version | Source |
|---|---|---|
| Kubernetes (kubeadm, kubelet, kubectl) | v1.37 (v1.37.1) | `pkgs.k8s.io/core:/stable:/v1.37` |
| containerd | 2.x (`containerd.io` from Docker's apt repository) | download.docker.com |
| Flannel | v0.28.9 | github.com/flannel-io/flannel releases |
| Minikube | v1.39.0 | github.com/kubernetes/minikube releases |
| MicroK8s | `1.36/stable` channel (latest stable track at the time of writing) | snapcraft.io/microk8s |
| Amazon EKS | Kubernetes 1.37 | AWS documentation |
| eksctl | v0.231.0 | github.com/eksctl-io/eksctl releases |
| AWS CLI | v2 | AWS documentation |
| Ubuntu | 24.04 LTS | |

Newer patch versions work the same way. When a new minor version is out, change the version in one place
(`K8S_MINOR` in [kubeadm/scripts/prepare-node.sh](kubeadm/scripts/prepare-node.sh), the repository line in the kubeadm
lesson) and run the tests.

## 8. AWS safety (EKS lesson)

- Everything is created in **one region** (`eu-central-1`) from one file ([eks/cluster.yaml](eks/cluster.yaml)),
  tagged `Project: k8s-from-zero`.
- [eks/scripts/inventory.sh](eks/scripts/inventory.sh) counts what exists in the region **before** you start and
  **after** cleanup; [eks/scripts/verify-cleanup.sh](eks/scripts/verify-cleanup.sh) proves nothing of the project is
  left (cluster, stacks, VPC, NAT gateway, Elastic IPs, load balancers, instances, volumes, IAM roles).
- Cost while running: about **$0.25–0.30 per hour**. Set an AWS Budget alert before you start, and delete the cluster
  the same day: [eks/cleanup.md](eks/cleanup.md).
- Never commit kubeconfig files, credentials or account IDs (`.gitignore` covers kubeconfig files).

## 9. How the tests work

[tests/mdrun.py](tests/mdrun.py) reads the Markdown lessons and runs every ```bash block in order, on the right machine
(`on=k8s-cp`, `on=k8s-worker`, ...). Annotations in HTML comments say what to expect (`contains=`, `absent=`, `fail`,
`retry=`); `--update` writes the real output into the ```text block under each command. In CI, GitHub-hosted runners
create the Ubuntu VMs with LXD (a small Multipass-compatible shim), so the lessons run unchanged. Details:
[tests/README.md](tests/README.md).

## 10. License

[MIT](LICENSE). Kubernetes, containerd, Flannel, Minikube, MicroK8s and eksctl are projects of their respective
owners; Amazon EKS and AWS are trademarks of Amazon.com, Inc. or its affiliates.
