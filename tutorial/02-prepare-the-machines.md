# 02 · Prepare the machines

> Goal: two Ubuntu 24.04 machines that Kubernetes can be installed on, and you know why every setting is there.
> Time: about 75 minutes. Level 2 of the [roadmap](../README.md#4-the-roadmap).

## Before you start

- Multipass works (`multipass version`).
- No VMs named `k8s-cp` or `k8s-worker` exist yet (`multipass list`). If they do from an earlier attempt, delete them
  with [kubeadm/cleanup.md](../kubeadm/cleanup.md) Level 3 and start fresh: half-prepared machines are the hardest to
  debug.

## The walk

### 1. Read docs/03 and docs/04 first (25 minutes)

[docs/03 · Installation prerequisites](../docs/03-installation-prerequisites.md) explains **why** each preparation step
exists. [docs/04 · The container runtime and the CRI](../docs/04-container-runtime-and-cri.md) explains what containerd
is and how the kubelet talks to it. Read them now; the steps below will feel like doing, not copying.

### 2. Step 1 of the lesson: create the machines

Open [kubeadm/README.md](../kubeadm/README.md) and run **Step 1**. Two `multipass launch` commands, then
`multipass list`.

Watch for: both machines in state `Running`, each with its own IPv4 address. Write the two addresses down; you will
meet them again in `kubectl get nodes -o wide`.

### 3. Step 2: prepare Ubuntu, on both machines

Run **Step 2a–2d** on **both** machines. This is where the 🖥️ markers matter: open two terminals, one with
`multipass shell k8s-cp`, one with `multipass shell k8s-worker`, and run each block in both.

What to watch for, and what it means:

| Step | You should see | If not |
|---|---|---|
| 2a hostname, IP, product_uuid | different values on the two machines | cloned VMs: recreate them; duplicate names or UUIDs break node identity |
| 2b swap | `swapon --show` prints nothing | the kubelet will refuse to start later |
| 2c modules and sysctls | `overlay` and `br_netfilter` loaded, `net.ipv4.ip_forward = 1` | Pod traffic will die between nodes: this is exactly troubleshooting lab 02 |
| 2d time | `System clock synchronized: yes` (can take a minute on fresh VMs) | certificates may look "not yet valid" |
| 2d firewall | `ufw` inactive | on real networks, open the ports in the table instead |

> **Senior habit:** after every block that changes configuration, there is a block that **reads it back**. Never trust
> that a command worked because it printed nothing. Read the state.

### 4. Step 3: containerd

Run **Step 3** on both machines. Two things deserve your full attention:

1. **The package's default config disables the CRI plugin.** That is not a bug: `containerd.io` is packaged for
   Docker, which does not need it. The lesson replaces the config with the complete default. If someone on your team
   skips this, `kubeadm init` fails at preflight. You will reproduce exactly that in
   [troubleshooting 03](../troubleshooting/03-kubeadm-init-failure.md).
2. **`SystemdCgroup = true`.** The kubelet and the runtime must use the same cgroup driver. Ubuntu 24.04 runs cgroup v2
   with systemd, so both use systemd. A mismatch shows up later as Pods restarting for no visible reason.

Watch for: `grep` prints a line with `SystemdCgroup = true`, and `systemctl is-active containerd` says `active`.

### 5. Step 4: kubeadm, kubelet, kubectl

Run **Step 4** on both. Watch for `kubeadm version -o short` printing a v1.37 version.

The lesson then tells you the kubelet "restarts every few seconds". Many beginners panic here and start reinstalling.
Don't. The kubelet has no configuration yet; `kubeadm init` (control plane) or `kubeadm join` (worker) gives it one.

## Expert commentary

- **Why it matters at work.** In real teams this chapter is a script, an Ansible role or a machine image, never manual
  typing. That is why the repository also has [kubeadm/scripts/prepare-node.sh](../kubeadm/scripts/prepare-node.sh):
  the same steps, automated. Read it after this chapter and compare it with what you typed. You will use it in lab 01.
- **Why `apt-mark hold`.** A routine `apt upgrade` must never upgrade Kubernetes behind your back. Cluster upgrades
  follow their own order (control plane first, then kubelets, one minor version at a time).
- **Common mistakes.** Running a block on one machine only; forgetting that `modprobe` alone does not survive a
  reboot (the files in `/etc/modules-load.d/` and `/etc/sysctl.d/` do); installing Ubuntu's containerd 1.7 package
  instead of 2.x.
- **What an interviewer asks.** "Why do you disable swap for Kubernetes?" "What is `br_netfilter` for?" "What is the
  CRI and why was dockershim removed?" "What is a cgroup driver?" All answered in docs/03 and docs/04.

## Checkpoint

You are done when, on **both** machines:

- [ ] swap is off and stays off after a reboot
- [ ] `overlay` and `br_netfilter` are loaded and the three sysctls are 1
- [ ] containerd is active and its config has `SystemdCgroup = true`
- [ ] `kubeadm`, `kubelet` and `kubectl` v1.37 are installed and held
- [ ] you can explain each of these four points to a colleague in one sentence

Next: [03 · Control plane and CNI](03-control-plane-and-cni.md)
