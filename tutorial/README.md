# The Kubernetes From Zero Training Course

This is the guided path through the whole repository. Think of it as a senior DevOps engineer sitting next to you
while you build four clusters: we decide what to run next, look at the output together, break things on purpose,
investigate, and fix them.

**The commands live in the lessons, not here.** Every chapter tells you which lesson (or which steps of it) to run
now, what to watch for while it runs, and what an experienced engineer thinks about when they see that output. The
lessons are tested end to end ([tests/](../tests/README.md)), so the commands you type are the ones that were proven
to work. The output excerpts quoted in this course are copied from those real runs.

| Chapter | What you do | Time |
|---|---|---|
| [00 · Start here](00-start-here.md) | Check your tools, clone the repo, tour it, understand the roadmap and how the tests prove the outputs | 30 min |
| [01 · Concepts](01-concepts.md) | What Kubernetes is, what it is made of, and the four ways to install it | 60 min |
| [02 · Prepare the machines](02-prepare-the-machines.md) | Two Ubuntu VMs: swap, kernel modules, sysctls, containerd 2.x, kubeadm v1.37 | 75 min |
| [03 · Control plane and CNI](03-control-plane-and-cni.md) | `kubeadm init`, kubeconfig, a `NotReady` node explained, Flannel | 45 min |
| [04 · Workers and verification](04-workers-and-verification.md) | `kubeadm join`, the verification checklist, a test app, a second worker | 75 min |
| [05 · Troubleshooting](05-troubleshooting.md) | Seven failures on your own cluster, investigated like an on-call engineer | 120 min |
| [06 · Minikube](06-minikube.md) | A cluster in a container, profiles, versions, add-ons, a Pod that does not fit | 75 min |
| [07 · MicroK8s](07-microk8s.md) | Kubernetes as one snap, add-ons, an Ingress on port 80 | 60 min |
| [08 · Amazon EKS](08-eks.md) | A managed cluster on AWS: costs, the console path, eksctl, a load balancer, verified teardown | 90 min |
| [09 · Cleanup and comparison](09-cleanup-and-compare.md) | Remove everything without leftovers; choose the right method for a situation | 45 min |
| [10 · Capstone](10-capstone.md) | 15 questions without notes, then a cluster with three faults and an incident note | 90 min |
| [11 · Knowledge check](11-knowledge-check.md) | The skills checklist per level and 20 self-test questions | 30 min |

About 13 hours in total, spread over as many sessions as you like. Chapters 02–05 use the same kubeadm cluster, so
plan them close together. Between sessions you can leave the VMs running, or stop them in Multipass and start them
again later: they keep their disks, so the cluster comes back.

## How to use it

1. Read a chapter top to bottom first. Then open the lesson it points to and run the steps.
2. Before you read the explanation of an output, look at your own terminal and say out loud what you think it means.
   Your guess is the training; the explanation is the correction.
3. When a troubleshooting lab says "don't fix it yet", don't. The investigation is the lesson.
4. Keep a notebook (a text file is fine): one line per error you met and what fixed it. That file becomes your own
   runbook.
5. Each chapter ends with a **checkpoint**. Don't move on until every item is true for you.

```text
 tutorial (why, what to watch)  ──►  lesson (the commands)  ──►  docs (the concept, in depth)
            ▲                                                          │
            └────────────── troubleshooting labs / challenges ◄────────┘
```

Ready? Open [00 · Start here](00-start-here.md).
