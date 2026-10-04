# 05 · Troubleshooting

> Goal: find the root cause of seven real failures from their symptoms, the way an on-call engineer does.
> Time: about 2 hours. Level 5 of the [roadmap](../README.md#4-the-roadmap).

## Before you start

Your two-node kubeadm cluster passes the verification checklist ([chapter 04](04-workers-and-verification.md#checkpoint)).
The test app `web` is still deployed. Labs 01–07 run on this cluster, **in order**: lab 03 creates an extra VM,
`k8s-lab`, that lab 04 uses and removes.

## The method first

Open [troubleshooting/README.md](../troubleshooting/README.md) and read "The general method". Every lab follows the
same nine headings:

```text
Problem → Symptoms → Initial investigation → Commands → Output interpretation → Root cause → Fix → Verification → Lesson learned
```

The method in five lines:

```text
 1. What exactly is the symptom?          kubectl get nodes / pods -A, read the STATUS column
 2. What does Kubernetes know about it?   kubectl describe <object>  → Conditions, Events
 3. What does the component say?          kubectl logs (--previous) / journalctl -u kubelet / -u containerd
 4. Which layer is it?                    network → runtime → kubelet → API server → workload configuration
 5. Change one thing, then verify         the same command that showed the symptom must now show it fixed
```

## How to work through each lab

1. Run the "Problem" block that breaks the cluster.
2. **Stop reading.** Look at the symptoms on your own. Write down your hypothesis in your notebook.
3. Then read the investigation and compare it with what you would have done.
4. Fix, verify, and write one line in your runbook: symptom → cause → fix.

## The walk

### Lab 01 · Node is NotReady

[01-node-not-ready.md](../troubleshooting/01-node-not-ready.md). The kubelet on the worker stops. It takes a little
while for the node to turn `NotReady`: the control plane waits for missed heartbeats before it reacts. In
`kubectl describe node` the `Ready` condition says `Kubelet stopped posting node status`, and the node gets an
`unreachable` taint. Remember that wording: in lab 07 the same `NotReady` has a different message.

### Lab 02 · Pod networking

[02-pod-networking.md](../troubleshooting/02-pod-networking.md). The nastiest kind of failure: **everything looks
healthy.** Nodes `Ready`, Pods `Running`, and yet `curl` to a Pod on the other node times out. The lab teaches you to
test inside the Pod, look at Flannel's interfaces (`flannel.1`, `cni0`) and routes, and finally read one sysctl. When
the dashboards are green and users still complain, this is the lab you will remember.

### Lab 03 · `kubeadm init` fails at preflight

[03-kubeadm-init-failure.md](../troubleshooting/03-kubeadm-init-failure.md). A fresh machine, prepared by a script
with one step skipped. The lesson is "running is not working": `systemctl` says containerd is `active`, but `crictl`
cannot use its CRI API. Always test a service the way its client uses it.

### Lab 04 · A worker cannot join

[04-worker-join-failure.md](../troubleshooting/04-worker-join-failure.md). An old join command from someone's notes.
The investigation goes from the bottom up: TCP to 6443 (`nc -zv`), the API server's `/version`, then the token list.
The lab also shows the other classic cause, a firewall, so you can tell the two apart in seconds. It ends by removing
`k8s-lab` properly.

### Lab 05 · kubectl cannot connect

[05-kubectl-connection.md](../troubleshooting/05-kubectl-connection.md). Two messages you will see in your first week
at any Kubernetes job: `localhost:8080 was refused` (no kubeconfig at all) and an `i/o timeout` to an address that does
not exist (wrong server in the kubeconfig). Your new first command when kubectl misbehaves:
`kubectl config current-context`, then `kubectl config view --minify`.

### Lab 06 · Core Pods are not running

[06-core-pods-not-running.md](../troubleshooting/06-core-pods-not-running.md). A one-letter typo in the CoreDNS
configuration, and new CoreDNS Pods go into `CrashLoopBackOff`. Notice that one old Pod keeps running: a rolling update
keeps the old version until the new one is healthy, which is why DNS still works at all. The tool chain is
`get` → `describe` → `logs --previous`. The lab also shows the habit that would have prevented it: back up a ConfigMap
before you edit it.

### Lab 07 · The container runtime is down

[07-container-runtime.md](../troubleshooting/07-container-runtime.md). `NotReady` again, but this time the kubelet is
alive and **reports** that the runtime is down. Same symptom as lab 01, different cause: that is why you read the
condition message instead of assuming.

### Then: lab 01 of the practical challenges

If you didn't do it in chapter 04, now is the moment for [labs/01 · add a second worker](../labs/01-kubeadm-installation.md).

## Expert commentary

- **Why it matters at work.** Nobody gets paid to install clusters every day; people get paid to fix them at 3 a.m.
  The method above, applied calmly, solves most incidents. Panic and random restarts make them worse and destroy the
  evidence.
- **Write the incident down.** Each lab's "Lesson learned" is a mini post-incident review. Get used to writing one: what
  broke, how you found out, the root cause, the fix, how to prevent it.
- **The chain to remember:**

  ```text
  kubectl ──► API server ◄──► kubelet ──CRI──► containerd ──► runc ──► container
                                  │
                                  └── CNI (Flannel) ──► Pod network ──► other nodes (ip_forward, VXLAN)
  ```

  Every lab broke one link of this chain. `NotReady` can be any link between kubelet and CNI; the message names it.
- **What an interviewer asks.** "A node is NotReady. What do you do?" "A Pod is in CrashLoopBackOff. Where do you look?"
  "Pods cannot talk across nodes but everything is green. Where do you start?" You now have real answers.

## Checkpoint

You are done when:

- [ ] you completed labs 01–07 and wrote one runbook line for each
- [ ] for at least four of them, your hypothesis was right **before** you read the investigation
- [ ] you can explain how lab 01 and lab 07 look the same in `kubectl get nodes` and different in `describe node`
- [ ] the cluster passes the verification checklist again (and `k8s-lab` is gone)

Keep the cluster if you want to do the [capstone](10-capstone.md) scenario on it later; otherwise remove it now with
[kubeadm/cleanup.md](../kubeadm/cleanup.md) (chapter 09 explains the cleanup levels).

Next: [06 · Minikube](06-minikube.md)
