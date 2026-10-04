# 01 · What is Kubernetes?

> Time: 15 minutes · No commands in this chapter: it explains what you are about to install, and why.

## The problem it solves

With Docker you can run an application in a container on **one** machine. Real applications quickly outgrow that:

- one machine is not enough, so containers must be spread over **many** machines
- a machine dies at 3 a.m., and its containers must start somewhere else, without a human
- the shop has 10 times more visitors on Black Friday, so it needs 10 more copies of the web server, then fewer again
- a new version must go live without downtime, and roll back if it is broken
- containers move between machines, so their IP addresses change all the time: how do they find each other?

Doing this by hand, or with scripts, does not scale. **Kubernetes** is the system that does it for you. It is an
open-source **container orchestrator**: you give it a group of machines and a description of what should run, and it
keeps reality matching that description.

## An analogy

Think of a large restaurant kitchen.

```text
  The head chef (control plane)                 The cooks (worker nodes)
  ┌───────────────────────────────┐             ┌──────────┐ ┌──────────┐ ┌──────────┐
  │ order book: "table 4 needs     │  assigns    │  cook 1  │ │  cook 2  │ │  cook 3  │
  │ 3 pizzas and 2 salads"        ├────────────►│ 2 pizzas │ │ 1 pizza  │ │ 2 salads │
  │ checks constantly: is every   │             └──────────┘ └──────────┘ └──────────┘
  │ order being cooked?            │◄──── "cook 2 went home sick" ──── the pizza is re-assigned
  └───────────────────────────────┘
```

The head chef does not cook. They keep the order book (the **desired state**), hand the work to cooks with free hands
(**scheduling**), and keep checking that every order is being cooked. If a cook leaves, the chef gives the work to
another one (**self-healing**). You talk only to the chef.

## What Kubernetes does

| Feature | What it means | You will see it in |
|---|---|---|
| **Desired state** | You declare *what* you want ("2 copies of nginx"), not *how* to do it | every `kubectl create deployment` |
| **Reconciliation** | Controllers compare desired and actual state in a loop, and fix the difference | the replacement Pods after a node fails |
| **Scheduling** | The scheduler picks a node with enough free CPU and memory for each Pod | [troubleshooting 08](../troubleshooting/08-insufficient-resources.md) |
| **Self-healing** | Crashed containers are restarted, Pods on dead nodes are replaced | [troubleshooting 01](../troubleshooting/01-node-not-ready.md) |
| **Service discovery** | A **Service** gives a group of Pods one stable name and IP; CoreDNS answers the name | the `web` Service in every lesson |
| **Rolling updates** | A new version replaces Pods a few at a time; a rollback is one command | `kubectl rollout status` |
| **Scaling** | Change the number of copies with one command, or automatically | `kubectl scale` |

The basic objects you will meet in the lessons:

```text
  Deployment "web"  ── "I want 2 copies of nginx:1.30-alpine"
      └── ReplicaSet ── keeps exactly 2 Pods alive
            ├── Pod web-…-abcde  (one or more containers, one IP)   on node A
            └── Pod web-…-fghij                                       on node B
  Service "web"  ── one stable address in front of all Pods with the label app=web
```

## What Kubernetes is not

- **Not a container runtime.** It does not run containers itself; it asks a runtime such as containerd to do it
  ([docs/04](04-container-runtime-and-cri.md)).
- **Not a way to build images.** You build images with Docker (or another builder) and push them to a registry.
- **Not a full platform out of the box.** Ingress controllers, storage drivers, monitoring, logging, CI/CD and backups
  are added on top. Clusters differ mostly in these extras.
- **Not always the right answer.** One small application on one server is simpler with Docker Compose. Kubernetes pays
  off when you have several services, several machines, or need high availability.

## Where Kubernetes runs

| Kind | Who runs the control plane | Examples | Used for |
|---|---|---|---|
| **Local** | you, on your computer | Minikube, MicroK8s, kind | learning, development, testing manifests |
| **Self-managed** | you, on your own machines or VMs | kubeadm, MicroK8s clusters, Rancher RKE2, k3s | on-premises, data centres, edge, full control |
| **Managed** | the cloud provider | Amazon EKS, Google GKE, Azure AKS | most production workloads in the cloud |

This course installs one of each: [kubeadm](../kubeadm/README.md) (self-managed, the "hard way made official"),
[Minikube](../minikube/README.md) and [MicroK8s](../microk8s/README.md) (local and lightweight), and
[Amazon EKS](../eks/README.md) (managed). The current Kubernetes version used throughout is **v1.37**.

## Real-world context

Most companies that run containers in production run them on Kubernetes, very often a managed service. As a DevOps
engineer you will be expected to: create clusters (with infrastructure as code), keep them updated, deploy applications
to them, and above all **troubleshoot** them when something goes wrong. Understanding what happens during installation
is the best preparation for troubleshooting: every component you install by hand here is one you will one day debug.

## Check yourself

<details><summary>1. What does "desired state" mean?</summary>

You describe what you want to exist (for example 2 copies of nginx), and Kubernetes works continuously to make the
actual state match it. You do not write the steps.
</details>

<details><summary>2. A node with 3 of your Pods is switched off. What happens?</summary>

The node becomes NotReady. After a timeout, the controllers notice the Pods are gone and the Deployment's ReplicaSet
creates replacement Pods, which the scheduler places on healthy nodes.
</details>

<details><summary>3. Why do applications use a Service instead of Pod IP addresses?</summary>

Pods are replaced all the time and every new Pod gets a new IP. A Service has a stable IP and DNS name and sends
traffic to whichever Pods currently match its label selector.
</details>

<details><summary>4. Does Kubernetes start the containers itself?</summary>

No. The kubelet on each node asks the container runtime (containerd in this course) through the CRI to start them.
</details>

<details><summary>5. When is Kubernetes probably overkill?</summary>

For a single small application on one server, where Docker Compose is simpler to run and to understand.
</details>

Next: [02 · Kubernetes architecture](02-kubernetes-architecture.md)
