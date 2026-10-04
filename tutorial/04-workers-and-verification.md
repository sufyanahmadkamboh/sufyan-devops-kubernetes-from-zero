# 04 · Workers and verification

> Goal: a two-node cluster that is **proven** to work, and then a third node you add on your own.
> Time: about 75 minutes. Level 4 of the [roadmap](../README.md#4-the-roadmap).

## Before you start

`k8s-cp` is `Ready` and all system Pods are `Running` ([chapter 03 checkpoint](03-control-plane-and-cni.md#checkpoint)).
`k8s-worker` is prepared (chapter 02) but not joined.

## The walk

### 1. Step 7 of the lesson: `kubeadm join`

Open [kubeadm/README.md](../kubeadm/README.md) at **Step 7**. A join needs three things, and the lesson explains each:

```text
 worker ──► API server address (where)  ──► bootstrap token (may I join?)  ──► CA cert hash (are you really my cluster?)
```

The lesson shows two ways: copy the command printed by `kubeadm token create --print-join-command` into a shell on the
worker, or let Multipass carry it from your computer in one line. Use whichever you understand better.

Watch for `This node has joined the cluster` at the end, then, back on k8s-cp, both nodes `Ready` in
`kubectl get nodes -o wide`. Compare the `INTERNAL-IP` column with the addresses you wrote down in chapter 02.

The `ROLES` column shows `<none>` for the worker. That column is only a label; the lesson adds it so the list is easier
to read. Labels are cheap and useful: real clusters label nodes by pool, zone and hardware.

### 2. Read docs/11 · The cluster verification checklist

Open [docs/11](../docs/11-cluster-verification.md). This is the checklist you will run after **every** installation in
this course, in the same order: nodes, system Pods, API health, DNS, a test workload, a Service from outside, Pod
traffic across nodes, version skew. Learn the order; it goes from the bottom of the stack to the top, so the first
failing check points at the broken layer.

### 3. Step 8: verify

Run **Step 8** of the lesson. Watch for:

| Check | What proves it |
|---|---|
| API server | `kubectl cluster-info` prints `Kubernetes control plane is running at https://...:6443` |
| health | `/readyz?verbose` ends with `readyz check passed` |
| workload | `web` deployment shows `2/2` |
| Service | `curl` through the worker's IP and NodePort prints `<title>Welcome to nginx!</title>` |
| Pod network | `curl` from k8s-cp to a **Pod IP** on the worker prints the same title |

Notice where the two `web` Pods run: both on `k8s-worker`. The control plane has a **taint** that keeps ordinary
workloads off it. That is deliberate: the control plane should not compete with applications for memory.

The last check is the one people forget. A cluster can look perfect (all nodes `Ready`, all Pods `Running`) while Pods
on different nodes cannot reach each other. Only a request across nodes proves the Pod network works. You will break
exactly this in troubleshooting lab 02.

### 4. Step 9 (optional): kubectl from your own computer

The lesson copies the kubeconfig out of the VM and uses it with `--kubeconfig`. This is how you will work with real
clusters: from your laptop, with a kubeconfig file per cluster or one file with several **contexts**. Keep that file
private; it is the admin key.

### 5. Your first challenge: lab 01 (now, or after chapter 05)

[labs/01 · add a second worker](../labs/01-kubeadm-installation.md) belongs to this level. The lab itself suggests doing
it after the troubleshooting labs, when you know how to debug a join that goes wrong; both orders work, because the lab
removes its extra node again at the end. Whenever you do it: **don't open the solution**. You have everything you need:
`prepare-node.sh` for the preparation, a fresh join command, a label, and a deployment with a node selector to prove the
new node runs Pods. Then remove the node cleanly: drain, delete, reset, delete the VM.

## Expert commentary

- **Why it matters at work.** Adding and removing nodes is routine operations work: capacity, hardware replacement,
  OS upgrades. The order (`drain` → `delete node` → `kubeadm reset` → remove the machine) protects running workloads.
- **Never reuse old join commands.** Bootstrap tokens expire after 24 hours by default. A join command from last
  week's notes is the number one cause of failed joins (troubleshooting lab 04).
- **Common mistakes.** Running `kubeadm join` without `sudo`; joining a worker whose preparation was skipped (it joins,
  then never becomes `Ready`); testing only from the node that runs the Pods, which hides network problems.
- **What an interviewer asks.** "How do you add a node to a kubeadm cluster?" "What is a taint, and why does the
  control plane have one?" "How do you check a cluster is healthy after an installation?"

## Checkpoint

You are done when:

- [ ] `kubectl get nodes` shows `k8s-cp` and `k8s-worker` both `Ready`
- [ ] the test app answers through the NodePort **and** a Pod on the worker answers from the control plane
- [ ] you can list the verification checklist in order and say what layer each check proves
- [ ] you completed lab 01 and removed `k8s-worker2` again (or planned it for after chapter 05)

Keep the cluster running: the next chapter breaks it.

Next: [05 · Troubleshooting](05-troubleshooting.md)
