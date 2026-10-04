# kubeadm · Cleanup

> Do this when you have finished the kubeadm lab and the [troubleshooting labs](../troubleshooting/README.md).

There are two levels of cleanup. Pick the one you need.

| Level | What it removes | When |
|---|---|---|
| 1. Remove the test workload | the `web` Deployment and Service | you want a clean cluster, but keep it |
| 2. Reset Kubernetes on the nodes | the cluster: certificates, etcd data, static Pods, kubelet config | you want to run `kubeadm init` again on the same machines |
| 3. Delete the machines | both VMs and everything on them | you are done with the lab |

## Level 1 · Remove the test workload (🖥️ on k8s-cp)

<!-- test: on=k8s-cp; contains=deleted -->
```bash
kubectl delete service web --ignore-not-found
kubectl delete deployment web --ignore-not-found
```

## Level 2 · Reset Kubernetes on the nodes

```text
⚠️ DESTRUCTIVE COMMAND
kubeadm reset removes this node's Kubernetes configuration: on the control plane that is the whole cluster
(certificates, etcd data with every object you created). Do not run it on a production system.
```

Remove the worker from the cluster first, so the control plane forgets it cleanly. `drain` moves its Pods away (here
there is nowhere to go, so they are simply deleted):

<!-- test: on=k8s-cp; contains=deleted -->
```bash
kubectl drain k8s-worker --ignore-daemonsets --delete-emptydir-data --force --timeout=120s
kubectl delete node k8s-worker
```

Reset the worker (🖥️ on k8s-worker). `kubeadm reset` stops the kubelet's work, removes the node's certificates and
`/etc/kubernetes` files, and cleans up what kubeadm created:

<!-- test: on=k8s-worker; contains=[reset] -->
```bash
sudo kubeadm reset -f
```

kubeadm tells you what it does **not** clean: the CNI configuration and the iptables rules. Remove them too, or the next
cluster on this machine inherits stale network settings:

<!-- test: on=k8s-worker -->
```bash
sudo rm -rf /etc/cni/net.d
sudo iptables -F && sudo iptables -t nat -F && sudo iptables -t mangle -F && sudo iptables -X
```

Then the control plane (🖥️ on k8s-cp). This deletes the cluster itself:

<!-- test: on=k8s-cp; contains=[reset] -->
```bash
sudo kubeadm reset -f
sudo rm -rf /etc/cni/net.d "$HOME/.kube"
sudo iptables -F && sudo iptables -t nat -F && sudo iptables -t mangle -F && sudo iptables -X
```

<!-- test: on=k8s-cp; fail; contains=refused -->
```bash
kubectl get nodes
```

The API server is gone, so kubectl cannot connect. The machines still have containerd, kubeadm, kubelet and kubectl
installed: you could run `kubeadm init` again right away.

## Level 3 · Delete the machines (on your computer)

```text
⚠️ DESTRUCTIVE COMMAND
This deletes both virtual machines and everything on them.
```

<!-- test: timeout=300 -->
```bash
multipass delete k8s-cp k8s-worker
multipass purge
```

<!-- test: absent=k8s-cp; absent=k8s-worker -->
```bash
multipass list
```

`multipass delete` moves the VMs to the trash; `multipass purge` removes them for good and frees the disk space.

Next: [Minikube](../minikube/README.md)
