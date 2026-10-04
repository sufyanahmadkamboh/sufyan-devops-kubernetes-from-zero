# 12 · Cleanup and reset

> Time: 15 minutes · Every lesson has its own cleanup page; this chapter explains the ideas behind them.

Creating a cluster is half the job. Removing it **completely** is the other half:

- **Cost.** A forgotten EKS cluster keeps billing every hour: control plane, nodes, NAT gateway, load balancer, public
  IPs ([10 · EKS](10-eks-architecture.md)). A forgotten Minikube or VM keeps eating your laptop's memory.
- **Leftover state.** A half-removed node keeps old certificates in `/etc/kubernetes`, CNI configuration in
  `/etc/cni/net.d` and iptables rules. The next `kubeadm init` or `join` then fails in confusing ways.
- **Confusion.** Stale kubeconfig contexts point kubectl at clusters that no longer exist
  ([troubleshooting 05](../troubleshooting/05-kubectl-connection.md)).

## The four levels

Clean up from the top down: the most specific things first, the machine last.

```text
 Level 1  Workloads     kubectl delete service/deployment ...        cluster keeps running, ready for more labs
 Level 2  Nodes         drain → delete node → reset the machine      cluster keeps running with fewer nodes
 Level 3  Cluster       kubeadm reset / minikube delete / snap remove / eksctl delete cluster
 Level 4  Machines      delete the VMs / check the cloud account is back to its starting state
```

Why the order matters: some level-1 objects create things **outside** the cluster. On EKS, a `Service type:
LoadBalancer` makes AWS create a load balancer, and a PersistentVolumeClaim makes an EBS volume. If you delete the
cluster first, nothing is left to delete them: they stay, keep billing, and the load balancer's network interfaces block
the VPC from being deleted.

## kubeadm

### Remove one node (level 2)

```text
⚠️ DESTRUCTIVE COMMAND · evicts every Pod from k8s-worker and removes the node from the cluster.
```

```bash
kubectl drain k8s-worker --ignore-daemonsets --delete-emptydir-data --force --timeout=120s
kubectl delete node k8s-worker
```

Then, on the worker itself:

```text
⚠️ DESTRUCTIVE COMMAND · removes all Kubernetes state from this machine.
```

```bash
sudo kubeadm reset -f
sudo rm -rf /etc/cni/net.d
sudo iptables -F && sudo iptables -t nat -F && sudo iptables -t mangle -F && sudo iptables -X
```

### What `kubeadm reset` does, and what it does not

| `kubeadm reset` removes | `kubeadm reset` leaves behind (you remove it) |
|---|---|
| static Pod manifests, certificates and kubeconfigs in `/etc/kubernetes` | CNI configuration in `/etc/cni/net.d` |
| the local etcd data (`/var/lib/etcd`) on a control plane | iptables / IPVS rules created by kube-proxy and the CNI |
| kubelet state (`/var/lib/kubelet`), stops the kubelet's Pods | `$HOME/.kube/config` of every user |
| | the installed packages (kubeadm, kubelet, kubectl, containerd) |
| | CNI network interfaces (`cni0`, `flannel.1`) until a reboot or `ip link delete` |

The command prints these reminders itself at the end. The full sequence for both machines is in
[kubeadm/cleanup.md](../kubeadm/cleanup.md).

### Remove the machines (level 4)

```text
⚠️ DESTRUCTIVE COMMAND · deletes the virtual machines and their disks.
```

```bash
multipass delete k8s-cp k8s-worker
multipass purge
```

## Minikube

```text
⚠️ DESTRUCTIVE COMMAND · deletes the "minikube" cluster: the container, its disk and its kubectl context.
```

```bash
minikube delete
```

| Variant | Removes |
|---|---|
| `minikube delete` | the default profile (node container, its volume, kubeconfig context) |
| `minikube delete -p multinode` | one named profile |
| `minikube delete --all` | every profile |
| `minikube delete --all --purge` | every profile **and** `~/.minikube` (cached images, downloaded binaries): the next start downloads everything again |

Details: [minikube/cleanup.md](../minikube/cleanup.md).

## MicroK8s

```text
⚠️ DESTRUCTIVE COMMAND · removes MicroK8s, its datastore and every workload on this machine.
```

```bash
sudo snap remove microk8s --purge
```

`--purge` skips the automatic snapshot snapd would otherwise keep of the snap's data, so nothing is left in
`/var/snap/microk8s`. On a multi-node cluster, first remove the other nodes (`microk8s leave` on the node, then
`microk8s remove-node <name>` on a remaining one). Then delete the VM as in the [lesson](../microk8s/README.md).

## Amazon EKS

The order from [eks/cleanup.md](../eks/cleanup.md):

```text
 1. kubectl delete service web          → AWS deletes the load balancer
    kubectl delete deployment web
 2. eks/scripts/verify-cleanup.sh | grep 'Load balancers'    wait until it says "gone"
 3. eksctl delete cluster -f eks/cluster.yaml --wait          → CloudFormation deletes node group, then cluster + VPC
 4. eks/scripts/verify-cleanup.sh       checks by name AND tag: cluster, stacks, VPC, NAT, EIPs, security groups,
                                        instances, volumes, load balancers, IAM roles
 5. eks/scripts/inventory.sh            the counts must equal the ones you saved before creating the cluster
```

```text
⚠️ DESTRUCTIVE COMMAND · deletes the EKS cluster k8s-from-zero, its nodes and the VPC eksctl created for it.
```

```bash
eksctl delete cluster -f eks/cluster.yaml --wait
```

`--wait` matters: without it eksctl returns while CloudFormation is still deleting, and you might believe it is done.
If a stack ends in `DELETE_FAILED`, the CloudFormation console shows which resource blocked it (almost always a
leftover load balancer or ENI in the VPC): delete that resource and run the command again.

## Verify, don't assume

Every cleanup page in this course ends with a command that **must fail or come back empty**:

| Cluster | Proof it is gone |
|---|---|
| kubeadm | `kubectl get nodes` → `connection refused`; `multipass list` no longer lists the VMs |
| Minikube | `docker ps -a --filter name=minikube` is empty; `kubectl config get-contexts minikube` fails |
| MicroK8s | `microk8s status` → command not found |
| EKS | `verify-cleanup.sh` → `Clean: nothing of k8s-from-zero is left.` and `inventory.sh` equals the "before" counts |

## Check yourself

<details><summary>Why delete a LoadBalancer Service before deleting an EKS cluster?</summary>

The AWS load balancer was created by Kubernetes, not by the eksctl CloudFormation stacks. Deleting the cluster first
leaves it running (and billing), and its network interfaces stop the VPC from being deleted.
</details>

<details><summary>After `kubeadm reset -f`, a new `kubeadm join` fails with network errors. What did reset leave behind?</summary>

CNI configuration in `/etc/cni/net.d`, iptables rules and CNI interfaces. Remove them (or reboot) before reusing the machine.
</details>

<details><summary>What is the difference between `minikube delete --all` and `minikube delete --all --purge`?</summary>

`--purge` also deletes `~/.minikube` (cached images and binaries), so the next start has to download everything again.
</details>

<details><summary>What does `drain` do before you delete a node?</summary>

It marks the node unschedulable and evicts its Pods (respecting PodDisruptionBudgets) so they are recreated on other
nodes; DaemonSet Pods are skipped with `--ignore-daemonsets`.
</details>

<details><summary>How do you prove an AWS account is back to its starting state?</summary>

Save a read-only inventory before creating anything, then compare it after cleanup, and check by tag and name for every
resource type the tool creates (the course's `inventory.sh` and `verify-cleanup.sh`). Also look at the bill the next day.
</details>

Next: [13 · Comparing the installation methods](13-installation-comparison.md)
