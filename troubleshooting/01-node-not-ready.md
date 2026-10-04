# 01 · A node is `NotReady`

> Uses the [kubeadm cluster](../kubeadm/README.md) (k8s-cp + k8s-worker). Time: 10 minutes.

## Problem

A colleague says: "The worker is broken. My Pods there stopped being updated." Let's reproduce it. Don't look at the
cause yet; we break it on purpose so you see the symptoms first.

<!-- test: on=k8s-worker -->
```bash
sudo systemctl stop kubelet
```

## Symptoms

Give the control plane about a minute, then look at the nodes:

<!-- test: on=k8s-cp; retry=60; contains=NotReady; output -->
```bash
kubectl get nodes
```

```text
NAME         STATUS     ROLES           AGE   VERSION
k8s-cp       Ready      control-plane   98s   v1.37.1
k8s-worker   NotReady   worker          62s   v1.37.1
```

`k8s-worker` is `NotReady`. The Pods on it still show `Running`, but nobody is checking on them any more:

<!-- test: on=k8s-cp; contains=k8s-worker; output -->
```bash
kubectl get pods -l app=web -o wide
```

```text
NAME                   READY   STATUS    RESTARTS   AGE   IP           NODE         NOMINATED NODE   READINESS GATES
web-6f5d6d9c94-2zks8   1/1     Running   0          51s   10.244.1.3   k8s-worker   <none>           <none>
web-6f5d6d9c94-fl5c7   1/1     Running   0          51s   10.244.1.2   k8s-worker   <none>           <none>
```

## Initial investigation

`NotReady` only tells you that the node's `Ready` condition is not `True`. The **reason** is in the node's conditions.
That is always the first place to look:

## Commands

<!-- test: on=k8s-cp; retry=20; contains=Kubelet stopped posting node status; output -->
```bash
kubectl describe node k8s-worker | sed -n '/Conditions:/,/Addresses:/p'
```

```text
Conditions:
  Type                 Status    LastHeartbeatTime                 LastTransitionTime                Reason              Message
  ----                 ------    -----------------                 ------------------                ------              -------
  NetworkUnavailable   False     Sun, 04 Oct 2026 14:46:58 +0000   Sun, 04 Oct 2026 14:46:58 +0000   FlannelIsUp         Flannel is running on this node
  MemoryPressure       Unknown   Sun, 04 Oct 2026 14:46:56 +0000   Sun, 04 Oct 2026 14:47:48 +0000   NodeStatusUnknown   Kubelet stopped posting node status.
  DiskPressure         Unknown   Sun, 04 Oct 2026 14:46:56 +0000   Sun, 04 Oct 2026 14:47:48 +0000   NodeStatusUnknown   Kubelet stopped posting node status.
  PIDPressure          Unknown   Sun, 04 Oct 2026 14:46:56 +0000   Sun, 04 Oct 2026 14:47:48 +0000   NodeStatusUnknown   Kubelet stopped posting node status.
  Ready                Unknown   Sun, 04 Oct 2026 14:46:56 +0000   Sun, 04 Oct 2026 14:47:48 +0000   NodeStatusUnknown   Kubelet stopped posting node status.
Addresses:
```

<!-- test: on=k8s-cp; retry=30; contains=unreachable; output -->
```bash
kubectl describe node k8s-worker | grep -A3 Taints
```

```text
Taints:             node.kubernetes.io/unreachable:NoExecute
                    node.kubernetes.io/unreachable:NoSchedule
Unschedulable:      false
Lease:
```

Now go to the node itself (🖥️ on k8s-worker) and ask systemd about the kubelet:

<!-- test: on=k8s-worker; contains=inactive; output -->
```bash
systemctl is-active kubelet || true
sudo journalctl -u kubelet --no-pager -n 3
```

```text
inactive
Oct 04 14:47:07 k8s-worker systemd[1]: kubelet.service: Deactivated successfully.
Oct 04 14:47:07 k8s-worker systemd[1]: Stopped kubelet.service - kubelet: The Kubernetes Node Agent.
Oct 04 14:47:07 k8s-worker systemd[1]: kubelet.service: Consumed 1.448s CPU time.
```

## Output interpretation

- Every condition is `Unknown` with the message **Kubelet stopped posting node status**: the control plane has not
  heard from this node's kubelet. The node did not report a problem; it stopped reporting at all.
- The node got the taint `node.kubernetes.io/unreachable`: after a grace period, Pods on it would be evicted and
  recreated elsewhere (if there were somewhere else to go).
- On the node, the kubelet is `inactive`, and the journal shows it was stopped.

## Root cause

The kubelet on the worker is not running, so nothing reports the node's status to the API server. (Here we stopped it;
in real life: a crash, a bad config after an upgrade, the node out of memory, or a reboot with the kubelet disabled.)

## Fix

<!-- test: on=k8s-worker -->
```bash
sudo systemctl start kubelet
```

## Verification

<!-- test: on=k8s-cp; retry=60; contains=k8s-worker; absent=NotReady; output -->
```bash
kubectl wait --for=condition=Ready node/k8s-worker --timeout=10s
kubectl get nodes
```

```text
node/k8s-worker condition met
NAME         STATUS   ROLES           AGE    VERSION
k8s-cp       Ready    control-plane   100s   v1.37.1
k8s-worker   Ready    worker          64s    v1.37.1
```

<!-- test: on=k8s-cp; retry=30; absent=unreachable -->
```bash
kubectl describe node k8s-worker | grep -A3 Taints
```

The node is `Ready` and the `unreachable` taint is gone.

## Lesson learned

`NotReady` is a symptom with several causes. Read the condition **message**, it tells you which one:

| Message in `kubectl describe node` | Likely cause | See |
|---|---|---|
| `Kubelet stopped posting node status` | kubelet stopped, node down, or the network between node and API server | this lab |
| `NetworkPluginNotReady ... cni plugin not initialized` | no CNI installed, or the CNI Pods are failing | [kubeadm Step 5](../kubeadm/README.md) |
| `container runtime is down` / `PLEG is not healthy` | containerd stopped or unhealthy | [07](07-container-runtime.md) |
| `MemoryPressure` / `DiskPressure` `True` | the node is out of memory or disk | [08](08-insufficient-resources.md) |

Next: [02 · Pod networking](02-pod-networking.md)
