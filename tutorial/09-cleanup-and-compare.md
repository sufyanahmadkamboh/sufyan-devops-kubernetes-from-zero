# 09 · Cleanup and comparison

> Goal: leave no cluster, VM, container or cloud resource behind, and be able to choose the right installation method
> for a situation and defend the choice. Time: about 45 minutes. Levels 9 and 10 of the
> [roadmap](../README.md#4-the-roadmap).

## Before you start

List what you still have running, so you know what this chapter will remove:

| Cluster | How to see it |
|---|---|
| kubeadm (`k8s-cp`, `k8s-worker`) and MicroK8s (`k8s-micro`) | `multipass list` |
| Minikube | `minikube profile list` |
| EKS | the inventory script from chapter 08, or the EKS console in your region |

If you want to do the [capstone](10-capstone.md) scenario, keep the kubeadm cluster until after chapter 10.

## The walk

### 1. Read docs/12 · Cleanup and reset

Open [docs/12](../docs/12-cleanup-and-reset.md). Cleanup has **levels**, and you choose the smallest one that does the
job:

```text
 1. workload   delete the Deployment and Service           the cluster stays
 2. node       drain, delete node, reset the machine        the cluster stays, one machine is free
 3. cluster    kubeadm reset / minikube delete / snap remove / eksctl delete
 4. machines   delete the VMs, or verify the cloud account is back to its starting state
```

Two facts from docs/12 to remember: `kubeadm reset` does **not** remove the CNI configuration, iptables rules or the
kubeconfig in your home folder; and on EKS, resources created by Kubernetes (load balancers) must go before the cluster.

### 2. Run every cleanup page, then its verification

| Cluster | Page | It is gone when |
|---|---|---|
| kubeadm | [kubeadm/cleanup.md](../kubeadm/cleanup.md) | `kubectl get nodes` is refused, then `multipass list` no longer shows the VMs |
| Minikube | [minikube/cleanup.md](../minikube/cleanup.md) | no `minikube` container left, and the kubectl context is gone |
| MicroK8s | [microk8s/cleanup.md](../microk8s/cleanup.md) | `microk8s status` fails, then the VM is gone |
| EKS | [eks/cleanup.md](../eks/cleanup.md) | `verify-cleanup.sh` says `Clean` and the inventory matches |

Every destructive command is announced with a `⚠️ DESTRUCTIVE COMMAND` box. Read the box **before** you run the
command, every time. That habit is worth more than any tool.

### 3. Read docs/13 · Comparing the installation methods

Open [docs/13](../docs/13-installation-comparison.md). You have now used all four, so the comparison table should read
like a summary of your own experience, not like theory. Pay attention to "Which one should I use?": the decision
starts with **who** the cluster is for (one developer, a pipeline, a fleet of devices, production traffic) and **who**
will operate it.

### 4. Lab 05 · Which installation for which situation?

Do [labs/05](../labs/05-installation-comparison.md): six situations, one choice each, two reasons and one risk. Write
your table first, then open the solution. Differences are fine if you can defend them; the reasoning is what counts.

## Expert commentary

- **Why it matters at work.** Leftovers cost money (cloud), break the next installation (stale CNI config, old
  certificates, iptables rules) or confuse colleagues (a context pointing at a cluster that no longer exists). Teams
  that clean up with verification steps have fewer "mystery" problems.
- **Choosing a method is a design decision.** In reviews you will be asked why you picked one. "Because I know it" is
  not an answer; "because the control plane must survive an AZ outage and we have no Kubernetes specialists on call" is.
- **Common mistakes.** Deleting VMs before `kubeadm reset` when the cluster is shared with other nodes; `minikube delete`
  in the wrong profile; running `eksctl delete` while a LoadBalancer Service exists.
- **What an interviewer asks.** "Which Kubernetes would you use for X and why?" "What does `kubeadm reset` leave
  behind?" "How do you make sure a cloud lab left nothing behind?"

## Checkpoint

You are done when:

- [ ] every cluster you created is removed and verified gone (except the one you keep for the capstone)
- [ ] you can list the four cleanup levels and say what `kubeadm reset` does not clean
- [ ] your lab 05 table has six rows with reasons and risks
- [ ] you can explain in two minutes when you would choose kubeadm, Minikube, MicroK8s or EKS

Next: [10 · Capstone](10-capstone.md)
