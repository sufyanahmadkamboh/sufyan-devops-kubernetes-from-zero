# 06 · CNI and Pod networking

> Time: 20 minutes · Background for Step 6 of the [kubeadm lesson](../kubeadm/README.md) and for
> [troubleshooting 02](../troubleshooting/02-pod-networking.md).

## The Kubernetes network model

Kubernetes sets three rules, and leaves the implementation to a plugin:

1. **Every Pod gets its own IP address.** Containers in one Pod share it (they reach each other on `localhost`).
2. **Every Pod can reach every other Pod**, on any node, **without NAT**: the IP a Pod sees for itself is the IP others
   use to reach it.
3. **Agents on a node** (kubelet, system daemons) can reach all Pods on that node.

Services (stable virtual IPs in front of Pods) are a separate layer, done by kube-proxy. Network policies (firewall
rules between Pods) are optional and must be supported by the plugin.

## What CNI is

The **Container Network Interface** is a small specification plus plugins. When the runtime creates a Pod's network
namespace, it calls the CNI plugin configured in `/etc/cni/net.d/`, with binaries in `/opt/cni/bin/`. The plugin:

- creates the Pod's network interface (`eth0` inside the Pod) and connects it to the node
- assigns the Pod an IP from the node's range (IPAM)
- makes sure other nodes know how to reach that range

## Why a node is NotReady without a CNI

Right after `kubeadm init`, `kubectl describe node` in the lesson shows (real output, Kubernetes 1.37):

```text
container runtime network not ready: NetworkReady=false reason:NetworkPluginNotReady
message:Network plugin returns error: cni plugin not initialized
```

The kubelet will not mark a node `Ready` until the runtime reports a working network, because Pods started there would
have no connectivity. CoreDNS stays `Pending` for the same reason. Installing Flannel fixes both within seconds.

## Flannel, as used in this course

**Flannel v0.28.9** is the simplest CNI: an overlay network, no network policies.

- Cluster Pod range **10.244.0.0/16** (that is why `kubeadm init --pod-network-cidr=10.244.0.0/16`).
- Each node gets a **/24** of it: for example `10.244.0.0/24` on the control plane, `10.244.1.0/24` on the worker.
- On each node: the bridge **`cni0`** connects local Pods; the VXLAN device **`flannel.1`** wraps packets for other
  nodes in UDP (port 8472).

A packet from a Pod on the control plane to a Pod on the worker:

```text
  k8s-cp                                                     k8s-worker
  ┌──────────────────────────────────┐                      ┌──────────────────────────────────┐
  │ Pod A 10.244.0.5                 │                      │                 Pod B 10.244.1.7 │
  │   │ eth0                         │                      │                         eth0 ▲   │
  │   ▼                              │                      │                              │   │
  │ cni0 bridge 10.244.0.1           │                      │           cni0 bridge 10.244.1.1 │
  │   │ route: 10.244.1.0/24 → flannel.1                    │                              ▲   │
  │   ▼                              │  UDP 8472 (VXLAN)    │                              │   │
  │ flannel.1 ── wraps packet ──► eth0 ─────────────────────► eth0 ──► flannel.1 unwraps ──┘   │
  │                     node IP 10.x.x.10                   node IP 10.x.x.11                  │
  └──────────────────────────────────┘                      └──────────────────────────────────┘
   requires on both nodes: net.ipv4.ip_forward = 1 (troubleshooting 02 turns it off)
```

## Other CNI plugins

| Plugin | How it works | Network policies | Typical use |
|---|---|---|---|
| **Flannel** | VXLAN overlay | no | learning, small clusters, k3s default |
| **Calico** | routed (BGP) or overlay (VXLAN/IP-in-IP), or eBPF data plane | yes | most self-managed production clusters; MicroK8s default |
| **Cilium** | eBPF in the kernel; can also replace kube-proxy | yes, also on layer 7 | large clusters, observability (Hubble), service mesh features |
| **Amazon VPC CNI** | no overlay: each Pod gets a **real IP from the VPC subnet**, as a secondary IP on the node's network interface | with the policy agent | EKS default (`aws-node` Pods in the lesson) |

## How to choose

```text
 Managed cloud cluster?          ──► use the provider's CNI (EKS: VPC CNI), unless you have a reason not to
 Need network policies?          ──► Calico or Cilium (not Flannel)
 Very large / need eBPF features ──► Cilium
 Learning, lab, minimal          ──► Flannel
```

Two practical consequences:

- The Pod range must **not overlap** with your node network or VPC, or packets go to the wrong place.
- On EKS with the VPC CNI, every Pod uses a VPC IP: small subnets limit how many Pods you can run, and each instance
  type has a maximum number of IPs (hence a maximum number of Pods per node).

## Check yourself

<details><summary>1. What are the three rules of the Kubernetes network model?</summary>

Every Pod has its own IP; all Pods can reach all Pods without NAT; node agents can reach the Pods on their node.
</details>

<details><summary>2. Why is a fresh kubeadm node NotReady?</summary>

No CNI plugin is installed, so the runtime reports `NetworkPluginNotReady` and the kubelet does not mark the node
Ready.
</details>

<details><summary>3. What are <code>cni0</code> and <code>flannel.1</code>?</summary>

`cni0` is the bridge connecting the Pods on one node; `flannel.1` is the VXLAN device that wraps packets for Pods on
other nodes.
</details>

<details><summary>4. What is special about Pod IPs on EKS with the VPC CNI?</summary>

They are real VPC addresses from the node's subnet, not an overlay. Anything in the VPC can route to them, and subnet
size limits the number of Pods.
</details>

<details><summary>5. You need network policies. Is Flannel a good choice?</summary>

No. Flannel does not enforce network policies. Choose Calico or Cilium.
</details>

Next: [07 · The four installation methods](07-installation-methods-overview.md)
