# 03 · Installation prerequisites (Linux)

> Time: 20 minutes · Read before the [kubeadm lesson](../kubeadm/README.md). Minikube, MicroK8s and EKS do these steps
> for you, but they still happen underneath.

A Linux machine does not become a Kubernetes node just by installing packages. The kernel, the network settings and
the resources must match what Kubernetes expects. Each step below says **what** to do and **why**. The repository
automates all of them in [kubeadm/scripts/prepare-node.sh](../kubeadm/scripts/prepare-node.sh).

## Checklist

| # | Requirement | Why | Check |
|---|---|---|---|
| 1 | **2 CPUs, about 2 GB RAM** or more on a control plane; a few GB of free disk | kubeadm's preflight refuses fewer than 2 CPUs or less than 1700 MB of memory: the control plane alone needs that much | `nproc`, `free -h`, `df -h /` |
| 2 | **Unique hostname, MAC address and product_uuid** | Nodes are identified by hostname; some components rely on unique MACs and the machine UUID. Cloned VMs often share them | `hostname`, `ip link`, `sudo cat /sys/class/dmi/id/product_uuid` |
| 3 | **Swap off** | By default the kubelet refuses to start with swap on: memory requests and limits assume real memory | `swapon --show` prints nothing |
| 4 | **Kernel modules `overlay` and `br_netfilter`** | `overlay`: the filesystem containerd uses for image layers. `br_netfilter`: lets iptables see traffic crossing Linux bridges, which Pod networking uses | `lsmod \| grep -E 'overlay\|br_netfilter'` |
| 5 | **sysctl `net.ipv4.ip_forward = 1`** | A node must route packets between Pods, other nodes and the outside. Off = Pods on different nodes cannot talk ([troubleshooting 02](../troubleshooting/02-pod-networking.md)) | `sysctl net.ipv4.ip_forward` |
| 6 | **sysctl `net.bridge.bridge-nf-call-iptables = 1`** (and `ip6tables`) | Service rules (kube-proxy) are iptables rules; bridged Pod traffic must pass through them | `sysctl net.bridge.bridge-nf-call-iptables` |
| 7 | **Time synchronised** | Certificates and tokens have validity periods; clocks that drift make TLS fail in confusing ways | `timedatectl` shows `System clock synchronized: yes` |
| 8 | **Required ports open between nodes** | See the table below | `nc -zv <ip> 6443` from another node |
| 9 | **A CRI container runtime, systemd cgroup driver** | The kubelet starts containers only through the CRI; kubelet and runtime must use the same cgroup driver | [docs/04](04-container-runtime-and-cri.md) |

Make module and sysctl settings permanent, or they are lost at the next reboot:

```text
/etc/modules-load.d/k8s.conf   overlay
                               br_netfilter
/etc/sysctl.d/k8s.conf         net.ipv4.ip_forward = 1
                               net.bridge.bridge-nf-call-iptables = 1
                               net.bridge.bridge-nf-call-ip6tables = 1
/etc/fstab                     swap line commented out
```

### About swap

Recent Kubernetes versions *can* run with swap (the kubelet's `NodeSwap` support, configured with `failSwapOn: false`
and a swap behaviour). It is an opt-in, advanced setup. For a first cluster, and for most production clusters today,
swap stays off.

## Ports

| Node | Port (TCP) | Used by | Who connects |
|---|---|---|---|
| control plane | **6443** | kube-apiserver | everyone: kubectl, kubelets, Pods |
| control plane | 2379–2380 | etcd client and peer API | API server, other etcd members |
| control plane | 10250 | kubelet API | API server (`kubectl logs`, `exec`) |
| control plane | 10257 | kube-controller-manager | itself (health) |
| control plane | 10259 | kube-scheduler | itself (health) |
| worker | 10250 | kubelet API | API server |
| worker | 30000–32767 | NodePort Services | clients of your applications |

Your CNI adds its own: Flannel's VXLAN uses **UDP 8472** between all nodes. In a cloud these ports are opened with
**security groups**; on-premises with the firewall (`ufw`, `firewalld`, `nftables`) or network ACLs. A blocked 6443 makes
a worker's `kubeadm join` hang ([troubleshooting 04](../troubleshooting/04-worker-join-failure.md)).

## cgroups and the cgroup driver

Linux **control groups (cgroups)** limit and account the CPU and memory of a group of processes: this is how a
container's `resources.limits` are enforced. Modern distributions (Ubuntu 24.04 included) use **cgroup v2** with
**systemd** as the manager of the cgroup tree.

The kubelet and the container runtime must use the **same cgroup driver**. Since Kubernetes 1.22 kubeadm configures
the kubelet with the `systemd` driver, so containerd must be set to systemd too (`SystemdCgroup = true`). Two managers
of the same tree = instability under resource pressure.

```text
            systemd (manages the cgroup tree)
             ├── kubelet.service           cgroupDriver: systemd
             └── kubepods.slice
                  └── kubepods-burstable-pod<uid>.slice
                       └── container (runc, via containerd: SystemdCgroup = true)
```

## Real-world context

In production these steps live in a machine image (Packer), cloud-init, or configuration management (Ansible), never
typed by hand. Managed node images such as the EKS-optimised Amazon Linux 2023 AMI ship with all of them done.

## Check yourself

<details><summary>1. Why must <code>net.ipv4.ip_forward</code> be 1?</summary>

The node must route packets from Pods to other nodes and outside. With forwarding off, cross-node Pod traffic is
dropped (troubleshooting 02 breaks it on purpose).
</details>

<details><summary>2. What does <code>br_netfilter</code> do?</summary>

It makes traffic crossing a Linux bridge visible to iptables, so the Service rules that kube-proxy writes also apply to
Pod traffic on the bridge.
</details>

<details><summary>3. Which port must a worker reach to join?</summary>

TCP 6443 on the control plane (the API server).
</details>

<details><summary>4. Two VMs were cloned from the same image. What can go wrong?</summary>

They can share the hostname, MAC address or product_uuid, which breaks node identity and networking. Check and fix
these before installing Kubernetes.
</details>

<details><summary>5. What happens if the kubelet uses the systemd cgroup driver and containerd uses cgroupfs?</summary>

Two different managers handle the same cgroups; the node becomes unstable under pressure. Set `SystemdCgroup = true`
in containerd so both use systemd.
</details>

Next: [04 · Container runtime and the CRI](04-container-runtime-and-cri.md)
