# Lab 01 · kubeadm: add a second worker

> After the [kubeadm lesson](../kubeadm/README.md) and the troubleshooting labs, before the cleanup. Time: 30 minutes.

## Task

The team needs more capacity. Add a third machine, `k8s-worker2`, to the cluster as a worker and prove that it
really runs workloads.

## Requirements

1. A new Ubuntu 24.04 machine `k8s-worker2` with 2 CPUs, 2 GB of memory and 15 GB of disk.
2. Prepared exactly like the first worker: swap off, kernel modules, sysctls, containerd 2.x with the systemd cgroup
   driver, kubeadm/kubelet/kubectl v1.37 held.
3. Joined with a **fresh** join command.
4. Labelled with the role `worker`.
5. At least one Pod of a new deployment runs on it.
6. Removed cleanly at the end (drain, delete, reset, delete the VM).

## Hints

- You don't have to repeat Steps 2–4 by hand: [kubeadm/scripts/prepare-node.sh](../kubeadm/scripts/prepare-node.sh)
  does exactly those steps. Read it before you run it.
- `kubeadm token create --print-join-command` on the control plane.
- `kubectl label node <name> node-role.kubernetes.io/worker=`
- To force Pods onto a node for a test: `kubectl get pods -o wide` shows where they run; scale up until one lands
  there, or use `nodeName` / a node selector.

## Expected result

`kubectl get nodes` shows three `Ready` nodes, `k8s-worker2` has the role `worker`, and `kubectl get pods -o wide`
shows a Pod of the test deployment on `k8s-worker2`.

## Solution

<details>
<summary>Try it yourself first. Then open the solution.</summary>

Create and prepare the machine (on your computer):

<!-- test: timeout=900 -->
```bash
multipass launch 24.04 --name k8s-worker2 --cpus 2 --memory 2G --disk 15G
```

<!-- test: timeout=1200; contains=ready: k8s-worker2 -->
```bash
multipass exec k8s-worker2 -- bash -s < kubeadm/scripts/prepare-node.sh
```

Join with a fresh command, then label the node:

<!-- test: timeout=600; contains=This node has joined the cluster; output=tail:4 -->
```bash
JOIN=$(multipass exec k8s-cp -- sudo kubeadm token create --print-join-command)
multipass exec k8s-worker2 -- sudo $JOIN
```

```text
...
* Certificate signing request was sent to apiserver and a response was received.
* The Kubelet was informed of the new secure connection details.

Run 'kubectl get nodes' on the control-plane to see this node join the cluster.
```

<!-- test: on=k8s-cp; retry=90; contains=k8s-worker2; absent=NotReady; output -->
```bash
kubectl wait --for=condition=Ready node/k8s-worker2 --timeout=10s
kubectl label node k8s-worker2 node-role.kubernetes.io/worker= --overwrite
kubectl get nodes
```

```text
node/k8s-worker2 condition met
node/k8s-worker2 labeled
NAME          STATUS   ROLES           AGE     VERSION
k8s-cp        Ready    control-plane   8m51s   v1.37.1
k8s-worker    Ready    worker          8m15s   v1.37.1
k8s-worker2   Ready    worker          9s      v1.37.1
```

Prove it runs workloads: a deployment pinned to the new node with a node selector (🖥️ on k8s-cp):

<!-- test: on=k8s-cp; contains=deployment.apps/capacity created -->
```bash
kubectl create deployment capacity --image=nginx:1.30-alpine --replicas=2
kubectl patch deployment capacity -p '{"spec":{"template":{"spec":{"nodeSelector":{"kubernetes.io/hostname":"k8s-worker2"}}}}}'
```

<!-- test: on=k8s-cp; retry=60; contains=successfully rolled out; output -->
```bash
kubectl rollout status deployment capacity --timeout=10s
kubectl get pods -l app=capacity -o wide
```

```text
Waiting for deployment "capacity" rollout to finish: 1 out of 2 new replicas have been updated...
Waiting for deployment "capacity" rollout to finish: 1 out of 2 new replicas have been updated...
Waiting for deployment "capacity" rollout to finish: 1 out of 2 new replicas have been updated...
Waiting for deployment "capacity" rollout to finish: 1 old replicas are pending termination...
Waiting for deployment "capacity" rollout to finish: 1 old replicas are pending termination...
Waiting for deployment "capacity" rollout to finish: 1 old replicas are pending termination...
deployment "capacity" successfully rolled out
NAME                        READY   STATUS        RESTARTS   AGE   IP           NODE          NOMINATED NODE   READINESS GATES
capacity-5d78bb8dcd-ckzbh   1/1     Running       0          1s    10.244.3.3   k8s-worker2   <none>           <none>
capacity-5d78bb8dcd-gt49p   1/1     Running       0          16s   10.244.3.2   k8s-worker2   <none>           <none>
capacity-78dd5f78bd-scw9g   1/1     Terminating   0          16s   10.244.1.8   k8s-worker    <none>           <none>
```

Clean up the exercise:

```text
⚠️ DESTRUCTIVE COMMAND · removes the node k8s-worker2 from the cluster and deletes its VM.
```

<!-- test: on=k8s-cp; contains=deleted -->
```bash
kubectl delete deployment capacity
kubectl drain k8s-worker2 --ignore-daemonsets --delete-emptydir-data --force --timeout=120s
kubectl delete node k8s-worker2
```

<!-- test: timeout=300 -->
```bash
multipass exec k8s-worker2 -- sudo kubeadm reset -f
multipass delete k8s-worker2
multipass purge
```

</details>

## Explanation

- Adding a worker is "prepare + join": every node needs the same runtime and packages; the control plane only needs to
  hand out a token. That is why the preparation is scripted: in real teams it is a script, an Ansible role or a
  machine image.
- `kubectl wait --for=condition=Ready` is better than looking at `get nodes` repeatedly: it fails clearly if the node
  never becomes Ready (look at the CNI Pod on that node, then the kubelet journal).
- The node selector `kubernetes.io/hostname` is a label every node gets automatically. Real clusters prefer custom
  labels (`pool=batch`) with taints and tolerations to dedicate nodes to workloads.
- Removing a node is always `drain` → `delete node` → `kubeadm reset` on the machine.

Next: [Lab 02 · Minikube](02-minikube-installation.md)
