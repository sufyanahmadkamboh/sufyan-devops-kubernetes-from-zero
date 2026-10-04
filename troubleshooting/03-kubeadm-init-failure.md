# 03 · `kubeadm init` fails at preflight

> Needs one fresh Ubuntu machine, `k8s-lab` (2 CPUs, 2 GB). Time: 15 minutes. It also covers investigating the
> **container runtime**, together with [07](07-container-runtime.md).

## Problem

A colleague prepared a new machine with a script and says: "kubeadm is broken, `init` fails immediately." Let's build
exactly that machine. Create it (on your computer):

<!-- test: timeout=900 -->
```bash
multipass launch 24.04 --name k8s-lab --cpus 2 --memory 2G --disk 15G
```

Your colleague's preparation, reproduced with the repository's [prepare-node.sh](../kubeadm/scripts/prepare-node.sh).
`CONFIGURE_CONTAINERD=no` makes it skip one step, the step your colleague forgot:

<!-- test: timeout=1200; contains=ready: k8s-lab -->
```bash
multipass exec k8s-lab -- env CONFIGURE_CONTAINERD=no bash -s < kubeadm/scripts/prepare-node.sh
```

Everything installed without an error. Now the moment of truth (🖥️ on k8s-lab):

<!-- test: on=k8s-lab; fail; contains=[ERROR; output=tail:8 -->
```bash
sudo kubeadm init --pod-network-cidr=10.244.0.0/16
```

```text
[init] Using Kubernetes version: v1.37.1
[preflight] Running pre-flight checks
[preflight] Some fatal errors occurred:
	[ERROR CRI]: could not connect to the container runtime: failed to create new CRI runtime service: validate service connection: validate CRI v1 runtime API for endpoint "unix:///var/run/containerd/containerd.sock": rpc error: code = Unimplemented desc = unknown service runtime.v1.RuntimeService
	[ERROR ContainerRuntimeVersion]: could not connect to the container runtime: failed to create new CRI runtime service: validate service connection: validate CRI v1 runtime API for endpoint "unix:///var/run/containerd/containerd.sock": rpc error: code = Unimplemented desc = unknown service runtime.v1.RuntimeService
[preflight] If you know what you are doing, you can make a check non-fatal with `--ignore-preflight-errors=...`
error: error execution phase preflight: preflight checks failed
To see the stack trace of this error execute with --v=5 or higher
```

## Symptoms

`kubeadm init` stops during the **preflight checks**, before it changes anything on the machine. The error is about the
container runtime: kubeadm cannot use the runtime through the CRI.

## Initial investigation

Don't reinstall anything yet. The message says "runtime". So: is containerd running? If it is, does it answer on the CRI?

## Commands

<!-- test: on=k8s-lab; contains=active; output -->
```bash
systemctl is-active containerd
containerd --version
```

```text
active
containerd containerd v2.3.6 ee2735368117d2eb259779949d5e75cdafec9761
```

containerd **is** running. Ask it something through the CRI, exactly like the kubelet would. `crictl` (installed with
kubeadm) is the CRI command-line client:

<!-- test: on=k8s-lab; fail; output -->
```bash
sudo crictl --runtime-endpoint unix:///run/containerd/containerd.sock version
```

```text
time="2026-10-04T14:49:36Z" level=warning msg="Config \"/etc/crictl.yaml\" does not exist, trying next: \"/usr/bin/crictl.yaml\""
time="2026-10-04T14:49:40Z" level=error msg="validate service connection: validate CRI v1 runtime API for endpoint \"unix:///run/containerd/containerd.sock\": rpc error: code = Unimplemented desc = unknown service runtime.v1.RuntimeService"
```

The CRI service is unknown or unimplemented. What does the configuration say?

<!-- test: on=k8s-lab; contains=disabled_plugins; output -->
```bash
grep -n 'disabled_plugins' /etc/containerd/config.toml
```

```text
15:disabled_plugins = ["cri"]
```

## Output interpretation

- `systemctl` says active: the **process** runs.
- `crictl` gets "unknown service" for the CRI runtime API: the **CRI plugin** is not loaded.
- The config file lists `cri` under `disabled_plugins`.

So the runtime is up, but the part of it Kubernetes talks to is switched off.

## Root cause

The `containerd.io` package from Docker's repository ships a configuration made for Docker, which does not need the
CRI plugin and disables it. The preparation skipped the step that replaces this file with the full default
configuration (and sets the systemd cgroup driver).

## Fix

Exactly Step 3 of the [kubeadm lesson](../kubeadm/README.md): write the complete default configuration, switch runc to
systemd cgroups, restart containerd.

<!-- test: on=k8s-lab; contains=SystemdCgroup = true -->
```bash
containerd config default | sudo tee /etc/containerd/config.toml > /dev/null
sudo sed -i 's/SystemdCgroup = false/SystemdCgroup = true/' /etc/containerd/config.toml
sudo systemctl restart containerd
grep -n 'SystemdCgroup' /etc/containerd/config.toml
```

## Verification

The CRI answers now:

<!-- test: on=k8s-lab; retry=10; contains=RuntimeName; output -->
```bash
sudo crictl --runtime-endpoint unix:///run/containerd/containerd.sock version
```

```text
time="2026-10-04T14:49:41Z" level=warning msg="Config \"/etc/crictl.yaml\" does not exist, trying next: \"/usr/bin/crictl.yaml\""
Version:  0.1.0
RuntimeName:  containerd
RuntimeVersion:  v2.3.6
RuntimeApiVersion:  v1
```

And kubeadm's preflight checks pass. `kubeadm init phase preflight` runs only the checks (and pulls the images), so this
machine stays free for the next lab, where it joins the existing cluster as a worker:

<!-- test: on=k8s-lab; timeout=900; contains=[preflight]; absent=[ERROR; output=tail:4 -->
```bash
sudo kubeadm init phase preflight
```

```text
[preflight] Running pre-flight checks
[preflight] Pulling images required for setting up a Kubernetes cluster
[preflight] This might take a minute or two, depending on the speed of your internet connection
[preflight] You can also perform this action beforehand using 'kubeadm config images pull'
```

## Lesson learned

- Read which **phase** failed: preflight failures happen before kubeadm changes anything, so fix and simply run it again.
- "Running" is not "working". Check the runtime the way the kubelet uses it: `crictl version`, `crictl info`.
- A package's default configuration is made for its most common use, not necessarily for yours.

Next: [04 · A worker cannot join](04-worker-join-failure.md)
