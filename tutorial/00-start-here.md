# 00 · Start here

> Check your tools, get the repository, find your way around it, and see the big picture. Time: about 30 minutes.

## What this course is

Kubernetes From Zero is an **installation lab**. You will not learn Kubernetes by reading about Deployments; you will
learn it by building the thing that runs them, four different ways, and then breaking it.

| You build | With | Why this one |
|---|---|---|
| a two-node cluster on Ubuntu | kubeadm | it shows every moving part; it is how self-managed clusters are built |
| a cluster in one container | Minikube | what developers use on laptops and in CI |
| a cluster from one package | MicroK8s | lightweight, edge devices, single machines |
| a managed cluster on AWS | Amazon EKS | what most companies run in production on AWS |

The application you deploy is always the same: two nginx Pods behind a Service. It is deliberately boring. The
**cluster** is the subject.

## Who it is for

You can use a terminal (`cd`, `ls`, `sudo`, editing a file) and you know what a container is. You have never installed
Kubernetes and you may never have used `kubectl`. That is exactly who this is for.

## Step 1 · Your tools

Open the main [README](../README.md#3-prerequisites) and go through the prerequisites table. Check each tool with the
command in the third column. You need:

- **Multipass** for the Ubuntu VMs (chapters 02–05 and 07)
- **Docker** for Minikube (chapter 06)
- **Git**
- for chapter 08 only: an AWS account you are allowed to spend money on. It is optional; the chapter also works as a
  read-along with the real recorded outputs.

> **Your computer matters.** The kubeadm cluster needs two VMs (2 CPUs and 4 GB, 2 CPUs and 3 GB). With 16 GB of RAM
> you are comfortable; with 8 GB, close everything else, and do the Minikube and MicroK8s chapters after you have
> deleted the kubeadm VMs.

## Step 2 · Get the repository

Clone it and open the folder in your editor. All lessons assume your terminal is in the **repository root**: some
commands read files like `kubeadm/scripts/prepare-node.sh` or `eks/cluster.yaml` by their relative path.

## Step 3 · The tour

```text
.
├── tutorial/          you are here: the guided path
├── docs/              13 concept lessons (read them when a chapter sends you there)
├── kubeadm/ minikube/ microk8s/ eks/
│                      the four installation lessons, each with its own cleanup page
├── troubleshooting/   8 labs: break it, investigate, fix, verify
├── labs/              5 practical challenges with hidden solutions
├── examples/nginx/    the test app as YAML files
├── capstone/          the final questions and scenario
└── tests/             the runner that executes every lesson
```

Open one installation lesson now, say [kubeadm/README.md](../kubeadm/README.md), and scroll through it without running
anything. Notice the shape. Every installation lesson follows the same 15 points: what it is, why it exists, when to
use it, what you need, a diagram of what we build, the steps, what happens during installation, verification, real
output, common errors, troubleshooting, cleanup, a challenge, real-world usage and key takeaways. Once you know the
shape, you always know where to look.

Notice also the little 🖥️ markers in the headings ("🖥️ on k8s-cp", "🖥️ on both"). They tell you **on which machine**
to type the commands. Half of all beginner mistakes in kubeadm labs are commands typed on the wrong machine.

## Step 4 · The roadmap

The [README roadmap](../README.md#4-the-roadmap) has ten levels. This course follows it:

| Level | Chapter |
|---|---|
| 1 Concepts | [01](01-concepts.md) |
| 2 Linux + runtime | [02](02-prepare-the-machines.md) |
| 3 kubeadm control plane | [03](03-control-plane-and-cni.md) |
| 4 Workers + verification | [04](04-workers-and-verification.md) |
| 5 Troubleshooting | [05](05-troubleshooting.md) |
| 6 Minikube | [06](06-minikube.md) |
| 7 MicroK8s | [07](07-microk8s.md) |
| 8 Amazon EKS | [08](08-eks.md) |
| 9 Cleanup and reset | [09](09-cleanup-and-compare.md) |
| 10 Compare + capstone | [09](09-cleanup-and-compare.md), [10](10-capstone.md), [11](11-knowledge-check.md) |

## Step 5 · Why you can trust the outputs

Every `bash` code block in the lessons is run by [tests/mdrun.py](../tests/mdrun.py). An HTML comment above each block
(you only see it in the raw Markdown) says where it runs and what the output must contain, for example
`<!-- test: on=k8s-cp; contains=NotReady -->`. In GitHub Actions, the runner creates real Ubuntu VMs and runs the
kubeadm, Minikube and MicroK8s lessons from top to bottom on every change. The EKS lesson was run once against a real
AWS account, recorded, and torn down. Details: [tests/README.md](../tests/README.md).

Two consequences for you:

1. If your output differs from the lesson's in **names, IPs, ages or hashes**, that is normal. If it differs in
   **status** (`NotReady` where the lesson says `Ready`, an error where the lesson has none), stop and investigate
   before you continue.
2. When a command fails for you, the problem is almost always in your environment (memory, a firewall, a VPN, a typo),
   not in the lesson. That is good news: it is a real troubleshooting exercise.

## Checkpoint

You are done when:

- [ ] `multipass version`, `docker version` and `git --version` all answer
- [ ] the repository is cloned and your terminal is in its root folder
- [ ] you can name the four installation methods and say in one sentence what each one is for
- [ ] you know what the 🖥️ markers mean

Next: [01 · Concepts](01-concepts.md)
