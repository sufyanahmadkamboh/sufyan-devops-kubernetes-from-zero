# 11 · Knowledge check

> Goal: see at a glance what you can do now, and find the gaps. Time: about 30 minutes.

## Skills checklist, by level

Tick what you can do **without looking it up**. Anything unticked: go back to the chapter in brackets.

**Level 1 · Concepts** ([01](01-concepts.md))
- [ ] Draw the control plane and a worker node with every component
- [ ] Explain the path of `kubectl apply` from kubectl to a running container

**Level 2 · Linux and runtime** ([02](02-prepare-the-machines.md))
- [ ] Prepare an Ubuntu machine: swap, kernel modules, sysctls, time, ports
- [ ] Install containerd 2.x with the CRI enabled and the systemd cgroup driver, and check it with `crictl`

**Level 3 · Control plane** ([03](03-control-plane-and-cni.md))
- [ ] Run `kubeadm init` and name its phases
- [ ] Explain why the node is `NotReady` until a CNI plugin is installed

**Level 4 · Workers and verification** ([04](04-workers-and-verification.md))
- [ ] Join a worker with a fresh join command; add and remove a node cleanly
- [ ] Run the verification checklist, including cross-node Pod traffic

**Level 5 · Troubleshooting** ([05](05-troubleshooting.md))
- [ ] Diagnose `NotReady` (kubelet vs runtime vs CNI) from `describe node`
- [ ] Diagnose `CrashLoopBackOff` with `describe` and `logs --previous`
- [ ] Debug a failed join from the bottom up; fix kubeconfig problems

**Level 6 · Minikube** ([06](06-minikube.md))
- [ ] Start, stop and delete clusters and profiles; pick a Kubernetes version
- [ ] Explain why a Pod is `Pending` from its Events

**Level 7 · MicroK8s** ([07](07-microk8s.md))
- [ ] Install from a pinned channel, enable add-ons, publish an app through an Ingress

**Level 8 · EKS** ([08](08-eks.md))
- [ ] Explain what AWS manages and what you manage; read a cluster's outputs and console
- [ ] Create from a file, verify, delete in the right order and prove nothing is left

**Level 9 · Cleanup** ([09](09-cleanup-and-compare.md))
- [ ] Choose the right cleanup level and verify it

**Level 10 · Decide** ([09](09-cleanup-and-compare.md), [10](10-capstone.md))
- [ ] Choose an installation method for a situation and defend it
- [ ] Fix a cluster with several faults and write the incident note

## 20 self-test questions

<details><summary>1. What does the kubelet do, and where does it run?</summary>

It runs on every node. It watches the API server for Pods assigned to its node, asks the container runtime (through the
CRI) to start their containers, runs their probes, and reports node and Pod status back. On kubeadm clusters it also
starts the control plane's static Pods. ([docs/02](../docs/02-kubernetes-architecture.md))
</details>

<details><summary>2. Why is etcd the most important thing to back up in a self-managed cluster?</summary>

etcd stores the whole cluster state: every object you created. Machines can be rebuilt from scripts; the state cannot.
On EKS, AWS takes care of it. ([docs/05](../docs/05-kubeadm-installation.md))
</details>

<details><summary>3. Name the two kernel modules and the three sysctls the lessons set, and why.</summary>

`overlay` (image layers for containerd) and `br_netfilter` (iptables sees bridged traffic); `net.ipv4.ip_forward = 1`
(the node routes Pod traffic), `net.bridge.bridge-nf-call-iptables = 1` and its IPv6 twin (bridged traffic goes through
iptables, where Service rules live). ([kubeadm Step 2c](../kubeadm/README.md))
</details>

<details><summary>4. What is the CRI, and which command talks to it directly?</summary>

The Container Runtime Interface, the API the kubelet uses to talk to a runtime such as containerd. `crictl` is its
command-line client: `crictl version`, `crictl ps`, `crictl info`. ([docs/04](../docs/04-container-runtime-and-cri.md))
</details>

<details><summary>5. Why must the kubelet and containerd use the same cgroup driver?</summary>

Both create and manage cgroups for the same containers. With two different managers (systemd and cgroupfs), resource
accounting becomes inconsistent and the node gets unstable. On systemd-based Ubuntu with cgroup v2, both use systemd
(`SystemdCgroup = true`). ([docs/04](../docs/04-container-runtime-and-cri.md))
</details>

<details><summary>6. Which three things does `kubeadm join` need?</summary>

The API server address, a valid bootstrap token, and the hash of the cluster's CA certificate (so the worker can verify
it is talking to the real control plane). `kubeadm token create --print-join-command` prints all three.
([kubeadm Step 7](../kubeadm/README.md))
</details>

<details><summary>7. What is a static Pod?</summary>

A Pod the kubelet starts directly from a manifest file on the node (`/etc/kubernetes/manifests` on kubeadm), not from
the API server. kubeadm runs the API server, etcd, the scheduler and the controller manager this way.
([docs/05](../docs/05-kubeadm-installation.md))
</details>

<details><summary>8. What does a CNI plugin do?</summary>

It gives every Pod a network interface and an IP address and makes Pods reachable from every node without NAT. Flannel
does it with an overlay (VXLAN); the Amazon VPC CNI gives Pods real VPC addresses. ([docs/06](../docs/06-cni-networking.md))
</details>

<details><summary>9. Why do the test Pods in the kubeadm lab never run on the control plane?</summary>

The control plane node carries a taint that only Pods with a matching toleration may ignore. It keeps workloads from
competing with the control plane for resources. ([kubeadm Step 8](../kubeadm/README.md))
</details>

<details><summary>10. Nodes Ready, Pods Running, but users get timeouts between services on different nodes. First suspects?</summary>

The Pod network between nodes: IP forwarding on a node, the CNI (Flannel's interfaces and routes), or a firewall
blocking the overlay traffic (UDP 8472 for Flannel VXLAN). Test with a request from one node to a Pod IP on the other.
([troubleshooting 02](../troubleshooting/02-pod-networking.md))
</details>

<details><summary>11. `The connection to the server localhost:8080 was refused` means?</summary>

kubectl found no kubeconfig and used its default address. Check `KUBECONFIG`, `~/.kube/config` and the current
context. ([troubleshooting 05](../troubleshooting/05-kubectl-connection.md))
</details>

<details><summary>12. What does `kubectl logs --previous` show, and when do you need it?</summary>

The output of the previous, crashed instance of a container. You need it for `CrashLoopBackOff`: the current instance
may not have logged anything yet. ([troubleshooting 06](../troubleshooting/06-core-pods-not-running.md))
</details>

<details><summary>13. A Pod is Pending with `Insufficient memory`. What exactly is insufficient?</summary>

The memory **requests**: on no node does allocatable memory minus the requests already placed leave enough for this
Pod's request. Real usage does not count. ([troubleshooting 08](../troubleshooting/08-insufficient-resources.md))
</details>

<details><summary>14. Where does the control plane run in Minikube, and in MicroK8s?</summary>

Minikube: inside the node container (kubeadm static Pods, as on a kubeadm node). MicroK8s: in one process, `kubelite`,
with dqlite as the datastore, so no control-plane Pods are visible. ([docs/08](../docs/08-minikube-internals.md),
[docs/09](../docs/09-microk8s-internals.md))
</details>

<details><summary>15. What is a kubeconfig context?</summary>

A named combination of a cluster (API server address and CA), a user (credentials) and a default namespace.
`kubectl config current-context` shows the active one, `use-context` switches.
([troubleshooting 05](../troubleshooting/05-kubectl-connection.md))
</details>

<details><summary>16. How does kubectl authenticate to EKS?</summary>

The kubeconfig entry runs `aws eks get-token` with your AWS identity on each request. EKS maps that identity to
Kubernetes permissions through access entries. ([eks Step 6](../eks/README.md))
</details>

<details><summary>17. What is the difference between a NodePort, a LoadBalancer Service and an Ingress?</summary>

NodePort opens the same port (30000–32767) on every node. LoadBalancer is a NodePort plus a cloud load balancer in
front. An Ingress is an HTTP rule (host/path → Service) executed by an ingress controller.
([labs/03](../labs/03-microk8s-installation.md), [labs/04](../labs/04-eks-installation.md))
</details>

<details><summary>18. Why delete LoadBalancer Services before deleting an EKS cluster?</summary>

Kubernetes created the load balancer, not eksctl. If the cluster goes first, nothing deletes it: it keeps costing
money and blocks the VPC deletion. ([eks/cleanup.md](../eks/cleanup.md))
</details>

<details><summary>19. What does `kubeadm reset` leave behind?</summary>

The CNI configuration in `/etc/cni/net.d`, iptables rules, and kubeconfig files in users' home folders. It also leaves
the packages and containerd installed. ([kubeadm/cleanup.md](../kubeadm/cleanup.md))
</details>

<details><summary>20. A team on AWS with no Kubernetes specialists needs production Kubernetes that survives an AZ outage. Which method?</summary>

Amazon EKS: AWS runs a multi-AZ control plane, and managed node groups can spread nodes over several AZs. The team still
owns node and add-on upgrades, IAM access and cost. ([labs/05](../labs/05-installation-comparison.md))
</details>

## What next?

- Repeat the kubeadm installation once more from memory, using only the lesson's headings as a guide.
- Read the [glossary](../study/glossary.md) and practise the [interview questions](../study/interview-questions.md)
  out loud.
- Go deeper on the areas this course only touches: cluster upgrades with `kubeadm upgrade`, etcd backup and restore,
  high-availability control planes ([docs/05 · Production is different](../docs/05-kubeadm-installation.md#production-is-different)).

Back to the [course overview](README.md).
