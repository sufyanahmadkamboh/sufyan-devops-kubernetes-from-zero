# Troubleshooting labs

Every lab **breaks something on purpose**, shows you the symptom exactly as you would meet it at work, and walks
through the investigation in the same order every time:

```text
Problem → Symptoms → Initial investigation → Commands → Output interpretation → Root cause → Fix → Verification → Lesson learned
```

All outputs shown in the labs are real: they were produced by running the labs end to end on fresh virtual machines.

| # | Lab | Cluster | What breaks | Main tools |
|---|---|---|---|---|
| 01 | [Node is NotReady](01-node-not-ready.md) | kubeadm | the kubelet stops on the worker | `kubectl describe node`, `systemctl`, `journalctl` |
| 02 | [Pod networking](02-pod-networking.md) | kubeadm | IP forwarding is switched off on a node | `curl`, `ip route`, `sysctl` |
| 03 | [kubeadm init fails](03-kubeadm-init-failure.md) | new VM | containerd's CRI plugin is disabled | `crictl`, `config.toml` |
| 04 | [Worker cannot join](04-worker-join-failure.md) | kubeadm + new VM | expired join token, blocked port 6443 | `nc`, `/version`, `kubeadm token list` |
| 05 | [kubectl cannot connect](05-kubectl-connection.md) | kubeadm | missing kubeconfig, wrong server address | `kubectl config` |
| 06 | [Core Pods not running](06-core-pods-not-running.md) | kubeadm | a typo in the CoreDNS configuration | `describe`, `logs --previous`, `rollout` |
| 07 | [Container runtime down](07-container-runtime.md) | kubeadm | containerd stops on the worker | `crictl`, `journalctl -u kubelet` |
| 08 | [Insufficient resources](08-insufficient-resources.md) | Minikube | too little memory for a cluster, a Pod that does not fit | `describe pod` events, node allocatable |

Labs 01–07 run on the two-node cluster of the [kubeadm lesson](../kubeadm/README.md), in this order (03 creates the
VM that 04 uses and removes). Lab 08 runs on the [Minikube](../minikube/README.md) cluster.

## The general method

```text
 1. What exactly is the symptom?          kubectl get nodes / pods -A, read the STATUS column
 2. What does Kubernetes know about it?   kubectl describe <object>  → Conditions, Events
 3. What does the component say?          kubectl logs (--previous) / journalctl -u kubelet / -u containerd
 4. Which layer is it?                    network → runtime → kubelet → API server → workload configuration
 5. Change one thing, then verify         the same command that showed the symptom must now show it fixed
```
