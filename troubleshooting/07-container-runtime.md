# 07 · The container runtime is down

> Uses the [kubeadm cluster](../kubeadm/README.md). Time: 10 minutes.

## Problem

The kubelet does not run containers itself; containerd does. What happens when containerd stops? Let's find out
(🖥️ on k8s-worker):

<!-- test: on=k8s-worker -->
```bash
sudo systemctl stop containerd
```

## Symptoms

<!-- test: on=k8s-cp; retry=90; contains=NotReady; output -->
```bash
kubectl get nodes
```

```text
NAME         STATUS     ROLES           AGE     VERSION
k8s-cp       Ready      control-plane   6m47s   v1.37.1
k8s-worker   NotReady   worker          6m11s   v1.37.1
```

The worker is `NotReady` again. Same symptom as in [lab 01](01-node-not-ready.md), but is it the same cause?

## Initial investigation

Read the condition message instead of assuming. Then check the kubelet and the runtime on the node.

## Commands

<!-- test: on=k8s-cp; retry=30; contains=runtime; output -->
```bash
kubectl describe node k8s-worker | grep -E '^\s+Ready\s'
```

```text
  Ready                False   Sun, 04 Oct 2026 14:52:57 +0000   Sun, 04 Oct 2026 14:52:57 +0000   KubeletNotReady              container runtime is down
```

This time the kubelet **is** reporting, and what it reports is a runtime problem. On the node (🖥️ on k8s-worker):

<!-- test: on=k8s-worker; contains=kubelet active; contains=containerd inactive; output -->
```bash
echo "kubelet $(systemctl is-active kubelet)"
echo "containerd $(systemctl is-active containerd || true)"
```

```text
kubelet active
containerd inactive
```

<!-- test: on=k8s-worker; fail; output -->
```bash
sudo crictl --runtime-endpoint unix:///run/containerd/containerd.sock ps
```

```text
time="2026-10-04T14:52:59Z" level=warning msg="Config \"/etc/crictl.yaml\" does not exist, trying next: \"/usr/bin/crictl.yaml\""
time="2026-10-04T14:53:03Z" level=error msg="validate service connection: validate CRI v1 runtime API for endpoint \"unix:///run/containerd/containerd.sock\": rpc error: code = Unavailable desc = connection error: desc = \"transport: Error while dialing: dial unix /run/containerd/containerd.sock: connect: no such file or directory\""
```

<!-- test: on=k8s-worker; contains=containerd.sock; output -->
```bash
sudo journalctl -u kubelet --no-pager --since "-2min" | grep -m 3 'containerd.sock'
```

```text
Oct 04 14:52:24 k8s-worker kubelet[3956]: W1004 14:52:24.281294    3956 logging.go:55] [core] [Channel #1 SubChannel #2] grpc: addrConn.createTransport failed to connect to {Addr: "/var/run/containerd/containerd.sock", ServerName: "localhost", }. Err: connection error: desc = "transport: Error while dialing: dial unix /var/run/containerd/containerd.sock: connect: no such file or directory"
Oct 04 14:52:24 k8s-worker kubelet[3956]: E1004 14:52:24.281445    3956 remote_runtime.go:435] "ListPodSandbox with filter from runtime service failed" err="rpc error: code = Unavailable desc = connection error: desc = \"transport: Error while dialing: dial unix /var/run/containerd/containerd.sock: connect: no such file or directory\"" filter=""
Oct 04 14:52:24 k8s-worker kubelet[3956]: E1004 14:52:24.281561    3956 generic.go:308] "GenericPLEG: Unable to retrieve pods" err="rpc error: code = Unavailable desc = connection error: desc = \"transport: Error while dialing: dial unix /var/run/containerd/containerd.sock: connect: no such file or directory\""
```

## Output interpretation

- Lab 01: `Kubelet stopped posting node status` → the **kubelet** was gone.
- Here: the kubelet is alive and reports that the **container runtime is down**. `crictl` cannot connect to
  `containerd.sock`, and the kubelet's log shows the same connection errors.

Note: the Pods' containers usually keep running for a while (each has its own `containerd-shim` process), but nothing
can be started, stopped or checked until the runtime is back.

## Root cause

containerd is not running on the worker (in real life: a crash, a broken configuration after an edit, a full disk,
or a package upgrade that went wrong).

## Fix

<!-- test: on=k8s-worker -->
```bash
sudo systemctl start containerd
```

If it does not start, `sudo journalctl -u containerd -n 50` shows why (most often a syntax error in
`/etc/containerd/config.toml`).

## Verification

<!-- test: on=k8s-cp; retry=90; contains=k8s-worker; absent=NotReady; output -->
```bash
kubectl wait --for=condition=Ready node/k8s-worker --timeout=10s
kubectl get nodes
```

```text
node/k8s-worker condition met
NAME         STATUS   ROLES           AGE     VERSION
k8s-cp       Ready    control-plane   7m6s    v1.37.1
k8s-worker   Ready    worker          6m30s   v1.37.1
```

<!-- test: on=k8s-worker; contains=CONTAINER; output=head:5 -->
```bash
sudo crictl --runtime-endpoint unix:///run/containerd/containerd.sock ps
```

```text
time="2026-10-04T14:53:18Z" level=warning msg="Config \"/etc/crictl.yaml\" does not exist, trying next: \"/usr/bin/crictl.yaml\""
CONTAINER           IMAGE               CREATED              STATE               NAME                ATTEMPT             POD ID              POD                        NAMESPACE
1c1e8f1cbd5e3       520212b8b0fcd       About a minute ago   Running             coredns             0                   5ed5c4accab88       coredns-644c598bdd-xt86q   kube-system
3dabd1809376d       43d9d8c1f8968       6 minutes ago        Running             nginx               0                   6287663861910       web-6f5d6d9c94-2zks8       default
641200fd387f2       43d9d8c1f8968       6 minutes ago        Running             nginx               0                   768b1546471a8       web-6f5d6d9c94-fl5c7       default
...
```

## Lesson learned

- The chain is: API server ⇄ **kubelet** → CRI → **containerd** → runc → containers. A `NotReady` node can be broken at
  any link; the condition message tells you which.
- Your node-level toolkit: `systemctl is-active kubelet containerd`, `journalctl -u kubelet`, `journalctl -u containerd`,
  `crictl ps`, `crictl info`.

Next: [08 · Insufficient resources](08-insufficient-resources.md)
