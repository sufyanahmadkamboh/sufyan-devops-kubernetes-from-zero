# 04 · The container runtime and the CRI

> Time: 20 minutes · Background for Step 3 of the [kubeadm lesson](../kubeadm/README.md) and for troubleshooting
> [03](../troubleshooting/03-kubeadm-init-failure.md) and [07](../troubleshooting/07-container-runtime.md).

## What a container runtime is

A **container runtime** is the software that actually runs containers on a machine: it pulls images, unpacks their
layers, sets up namespaces and cgroups, and starts the process. Two layers are involved:

```text
 kubelet ──CRI (gRPC over a Unix socket)──► containerd  ──► containerd-shim ──► runc ──► your container process
            high-level runtime: images, snapshots,           low-level runtime: creates the namespaces and
            containers, the CRI service                     cgroups through the Linux kernel, then exits
```

- **High-level runtime** (containerd, CRI-O): manages images and container lifecycles, and serves the CRI.
- **Low-level runtime** (runc, crun): the small program that really creates the container, following the OCI spec.

## The CRI

The **Container Runtime Interface** is a gRPC API that the kubelet uses to talk to *any* runtime: "run this Pod sandbox",
"pull this image", "start this container", "list containers". Any runtime that implements it works with Kubernetes. For
containerd the socket is `unix:///run/containerd/containerd.sock`.

## Why Docker is not used directly (dockershim)

Docker Engine predates the CRI and never implemented it. For years the kubelet contained an adapter, **dockershim**,
to translate. It was removed in **Kubernetes 1.24** (2022). What that means in practice:

- Kubernetes talks to containerd (or CRI-O) directly. Docker itself also uses containerd underneath.
- **Images built with Docker work unchanged**: they are standard OCI images.
- On a node, `docker ps` shows nothing of Kubernetes. Use `crictl`.

## containerd vs CRI-O

| | containerd | CRI-O |
|---|---|---|
| Origin | split out of Docker, CNCF graduated | built only for Kubernetes (Red Hat), CNCF graduated |
| Scope | general-purpose (Docker, BuildKit, nerdctl also use it) | only what the CRI needs |
| Where you meet it | most distributions, EKS, GKE, AKS, Minikube, MicroK8s, kubeadm guides | OpenShift, Fedora/RHEL-based clusters |

Both are fine choices. This course uses **containerd 2.x** everywhere.

## containerd 2.x configuration

Ubuntu 24.04's own `containerd` package is the 1.x series. Kubernetes 1.37 is the last release line that supports
containerd 1.x, so the lessons install `containerd.io` (2.x) from Docker's apt repository.

Two configuration traps, both in `/etc/containerd/config.toml`:

1. **The `containerd.io` package ships a config made for Docker**, with `disabled_plugins = ["cri"]`. containerd runs,
   but the CRI service is off and kubeadm's preflight fails. Fix: generate the full default config with
   `containerd config default`. Reproduced on purpose in [troubleshooting 03](../troubleshooting/03-kubeadm-init-failure.md).
2. **The cgroup driver.** runc must use systemd cgroups, matching the kubelet. In containerd 2.x (config version 3) the
   setting lives here:

```text
[plugins.'io.containerd.cri.v1.runtime'.containerd.runtimes.runc.options]
  SystemdCgroup = true
```

(In containerd 1.x the path was `[plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc.options]`; old blog
posts still show it. In 2.x that section no longer applies.)

The lesson's three lines:

```bash
containerd config default | sudo tee /etc/containerd/config.toml > /dev/null
sudo sed -i 's/SystemdCgroup = false/SystemdCgroup = true/' /etc/containerd/config.toml
sudo systemctl restart containerd
```

## crictl vs docker vs nerdctl

| Tool | Talks to | Use it for |
|---|---|---|
| `crictl` | any CRI runtime, through the CRI socket | **debugging Kubernetes nodes**: `crictl ps`, `crictl pods`, `crictl logs`, `crictl info`, `crictl images` |
| `docker` | Docker Engine | building and running containers on your computer; not present on a kubeadm node |
| `nerdctl` | containerd directly (Docker-like commands) | working with containerd without Docker; sees Kubernetes containers in the `k8s.io` namespace |
| `ctr` | containerd directly (low level) | containerd's own debug client; not user friendly |

`crictl` is installed with the Kubernetes packages (`cri-tools`). Pass the endpoint, or set it once in
`/etc/crictl.yaml`:

```bash
sudo crictl --runtime-endpoint unix:///run/containerd/containerd.sock ps
```

## Typical runtime failures

| Symptom | Likely cause | Lab |
|---|---|---|
| `kubeadm init` preflight: container runtime is not running / CRI v1 not implemented | CRI plugin disabled in `config.toml` | [03](../troubleshooting/03-kubeadm-init-failure.md) |
| Node `NotReady`, kubelet log: cannot connect to `containerd.sock` | containerd stopped or crashing | [07](../troubleshooting/07-container-runtime.md) |
| Pods restart randomly under load, kubelet warnings about cgroups | cgroup driver mismatch | Step 3 of the kubeadm lesson |
| `ErrImagePull` / `ImagePullBackOff` | wrong image name/tag, no registry access, missing pull secret | `kubectl describe pod` events |

## Check yourself

<details><summary>1. What is the CRI?</summary>

The gRPC API the kubelet uses to talk to any container runtime: run Pod sandboxes, pull images, start and list
containers.
</details>

<details><summary>2. Do images built with Docker still run on Kubernetes after dockershim was removed?</summary>

Yes. Docker builds standard OCI images, which containerd and CRI-O run unchanged. Only Docker Engine as the node's
runtime was dropped.
</details>

<details><summary>3. containerd is "active" but kubeadm says the runtime is not usable. What do you check?</summary>

Whether the CRI answers: `sudo crictl --runtime-endpoint unix:///run/containerd/containerd.sock version`, and whether
`config.toml` lists `cri` under `disabled_plugins`.
</details>

<details><summary>4. Why does <code>docker ps</code> show nothing on a kubeadm node?</summary>

Docker is not installed; Kubernetes runs its containers through containerd. Use `crictl ps`.
</details>

<details><summary>5. Where is the SystemdCgroup setting in containerd 2.x?</summary>

Under `[plugins.'io.containerd.cri.v1.runtime'.containerd.runtimes.runc.options]`.
</details>

Next: [05 · What kubeadm does](05-kubeadm-installation.md)
