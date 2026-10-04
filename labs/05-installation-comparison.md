# Lab 05 · Which installation for which situation?

> After all four installation lessons and [docs/13](../docs/13-installation-comparison.md). Time: 20 minutes. No
> commands: this is the decision an engineer is asked to make (and to defend) in design reviews and interviews.

## Task

For each of the six situations below, choose **kubeadm**, **Minikube**, **MicroK8s** or **Amazon EKS** (or say why
none fits), and give two reasons and one risk.

## Requirements

1. A developer wants to test their Helm chart on their Windows laptop before opening a pull request.
2. A CI pipeline must run integration tests against a real Kubernetes API on every pull request, in under 5 minutes.
3. A factory has 40 small industrial PCs (4 GB RAM each) running Ubuntu, one cluster per production line, no
   internet most of the time, a single technician on site.
4. A start-up runs its customer-facing API on AWS; two engineers, no on-call Kubernetes specialist; must survive the
   loss of an availability zone.
5. A bank must run Kubernetes in its own data centre, on its own hardware, with full control over every component
   and certificate.
6. You are preparing for the CKA exam.

## Hints

- What is managed for you, and what do you operate yourself? (control plane, etcd, upgrades, certificates, nodes)
- Who is the user: one person on one machine, a pipeline, a fleet of devices, or production traffic?
- High availability: which methods can run more than one control-plane node, and which give you that by default?
- Cost: hourly cloud cost vs hardware you already own vs people's time.

## Expected result

A table with one row per situation: choice, two reasons, one risk. There is more than one defensible answer; the
reasoning is what counts.

## Solution

<details>
<summary>Try it yourself first. Then open the solution.</summary>

| # | Choice | Reasons | Risk |
|---|---|---|---|
| 1 | **Minikube** | runs on Windows with Docker Desktop; full cluster in one command, deleted in one command; add-ons (ingress, metrics-server) like a real cluster | the laptop needs ~2 CPUs and 2+ GB free for it; single node hides scheduling and networking issues |
| 2 | **Minikube** (or kind) | `minikube start` took 35 s in this repository's CI run (GitHub-hosted runner, Docker driver); a fresh cluster per run, nothing to clean up | cluster start time on every run; the test cluster's version must match production |
| 3 | **MicroK8s** | snap install on Ubuntu, small footprint, add-ons, automatic HA with 3+ nodes, works offline once installed (`snap download` for air-gapped installs) | automatic snap refreshes must be controlled (`snap refresh --hold` / a fixed channel); a 4 GB machine leaves little room for workloads |
| 4 | **Amazon EKS** | AWS runs a multi-AZ control plane, etcd, upgrades of the control plane, certificates; managed node groups across AZs; integrates with IAM, load balancers, EBS | cost (control plane + nodes + NAT + LB) and AWS-specific pieces (VPC CNI IP use, access entries); you still upgrade nodes and add-ons |
| 5 | **kubeadm** | the upstream, conformant way to build a cluster on your own machines; full control over certificates, etcd, CNI, versions; HA with 3 control planes and a load balancer | you operate everything: etcd backups, certificate renewal, upgrades, OS patching; needs real Kubernetes skills on the team |
| 6 | **kubeadm** | the CKA exam tasks use kubeadm clusters (install, join, upgrade, etcd backup); you learn every component | takes longer to build, and mistakes teach a lot (exactly the [troubleshooting labs](../troubleshooting/README.md)) |

</details>

## Explanation

The four tools are not competitors: they solve different problems.

```text
                 one machine, short-lived            many machines, long-lived
              ┌───────────────────────────────┬───────────────────────────────────┐
 you operate  │ Minikube  (laptops, CI)       │ kubeadm   (your servers, exams)   │
 everything   │ MicroK8s  (single box, edge)  │ MicroK8s  (edge/IoT fleets, HA)   │
              ├───────────────────────────────┼───────────────────────────────────┤
 cloud runs   │            —                  │ EKS (or AKS / GKE)                │
 the control  │                               │ production on AWS                 │
 plane        │                               │                                   │
              └───────────────────────────────┴───────────────────────────────────┘
```

Most companies use two of them at the same time: a local cluster (Minikube, kind, MicroK8s) for development and
CI, and a managed cluster (EKS, AKS, GKE) for production. kubeadm is what you use when you must own the whole stack,
and what all of the others are compared to.

Back to the [roadmap](../README.md).
