# Interview questions

25 questions that come up in interviews for junior and intermediate DevOps, platform and cloud roles. Answer each one
out loud first, then open the model answer. Each answer links to the lesson where you did it yourself: in an interview,
"I did this in a lab, and here is what I saw" beats any memorised definition.

## Fundamentals

<details><summary>1. What problem does Kubernetes solve?</summary>

Running containers on one machine is easy; running many containers across many machines reliably is not. Kubernetes
places containers on machines, restarts them when they fail, replaces machines that disappear, gives them stable
addresses and names, and rolls out new versions gradually. You declare the desired state, and controllers keep reality
matching it. ([docs/01](../docs/01-what-is-kubernetes.md))
</details>

<details><summary>2. Describe the components of a Kubernetes cluster.</summary>

The control plane has the API server (the only entry point), etcd (the state), the scheduler (chooses nodes for Pods)
and the controller manager (the reconciliation loops), plus a cloud controller manager on clouds. Every node runs the
kubelet (starts and watches Pods), kube-proxy (Service rules) and a container runtime such as containerd. Add-ons such
as CoreDNS and a CNI plugin complete it. ([docs/02](../docs/02-kubernetes-architecture.md))
</details>

<details><summary>3. What happens when you run `kubectl apply -f deployment.yaml`?</summary>

kubectl sends the object to the API server, which authenticates, authorises, validates and stores it in etcd. The
Deployment controller creates a ReplicaSet, which creates Pod objects. The scheduler assigns each Pod to a node. The
kubelet on that node sees the Pod, asks containerd through the CRI to pull the image and start the containers, and
reports the status back. ([docs/02](../docs/02-kubernetes-architecture.md))
</details>

<details><summary>4. What is etcd, and why is it critical?</summary>

etcd is a distributed key-value store that holds every object in the cluster. If it is lost without a backup, the
cluster's entire state is lost, even if all the machines are fine. On self-managed clusters you back it up regularly
and test restores; on managed services such as EKS, the provider does it. ([docs/05](../docs/05-kubeadm-installation.md))
</details>

## Installation

<details><summary>5. What do you have to prepare on a Linux machine before running kubeadm?</summary>

Unique hostname, MAC and product_uuid; swap off; the `overlay` and `br_netfilter` kernel modules; IP forwarding and
bridged traffic through iptables; synchronised time; open ports (6443, 10250, etcd and the NodePort range); a container
runtime with the CRI enabled and the systemd cgroup driver; and kubeadm, kubelet and kubectl of the same minor version,
held against accidental upgrades. ([kubeadm Steps 1–4](../kubeadm/README.md))
</details>

<details><summary>6. Why was "Docker support" removed from Kubernetes, and does that mean Docker images no longer work?</summary>

Docker Engine does not implement the CRI, so Kubernetes maintained an adapter called dockershim, which was removed in
1.24. Kubernetes now talks directly to CRI runtimes such as containerd or CRI-O. Images built with Docker are standard
OCI images and run unchanged. ([docs/04](../docs/04-container-runtime-and-cri.md))
</details>

<details><summary>7. Walk me through what `kubeadm init` does.</summary>

It runs preflight checks, creates a certificate authority and the component certificates, writes kubeconfig files, and
writes static Pod manifests for the API server, etcd, scheduler and controller manager, which the kubelet then starts.
It waits for the API server, stores its configuration in the cluster, taints the control-plane node, creates a
bootstrap token, and installs CoreDNS and kube-proxy. Its output ends with the next steps: kubeconfig, a CNI plugin, and
the join command. ([docs/05](../docs/05-kubeadm-installation.md))
</details>

<details><summary>8. How does a new node join a kubeadm cluster securely?</summary>

It needs the API server address, a bootstrap token and the CA certificate hash. The token proves to the cluster that
the node may join; the hash lets the node verify it is talking to the real control plane. The kubelet then gets its own
client certificate through TLS bootstrapping. `kubeadm token create --print-join-command` produces a fresh command.
([kubeadm Step 7](../kubeadm/README.md))
</details>

<details><summary>9. When would you use Minikube, MicroK8s, kubeadm or a managed service?</summary>

Minikube for development and CI: a disposable cluster in one command. MicroK8s for single machines, edge and IoT fleets:
one package, small footprint, optional HA. kubeadm when you must run Kubernetes on your own machines with full control,
and to learn the internals. A managed service such as EKS for production in the cloud, when you want the provider to
run a highly available control plane. ([docs/13](../docs/13-installation-comparison.md), [labs/05](../labs/05-installation-comparison.md))
</details>

<details><summary>10. How does a production kubeadm cluster differ from the lab?</summary>

Three or more control-plane nodes behind a load balancer (`--control-plane-endpoint`), possibly external etcd, several
workers in different failure domains, regular etcd backups, certificate renewal, a tested upgrade process, hardening,
monitoring and persistent storage. The lab has one of each to show the mechanics.
([docs/05 · Production is different](../docs/05-kubeadm-installation.md#production-is-different))
</details>

## Networking

<details><summary>11. Explain the Kubernetes network model.</summary>

Every Pod gets its own IP address; every Pod can reach every other Pod on any node without NAT; agents on a node can
reach all Pods on that node. Kubernetes defines the model but does not implement it: a CNI plugin does.
([docs/06](../docs/06-cni-networking.md))
</details>

<details><summary>12. Why is a freshly initialised node `NotReady`?</summary>

No CNI plugin is installed yet. The kubelet reports `NetworkReady=false reason:NetworkPluginNotReady ... cni plugin not
initialized`, and CoreDNS stays Pending for the same reason. Installing a CNI matching the Pod CIDR, Flannel in the lab,
makes the node Ready. ([kubeadm Steps 5–6](../kubeadm/README.md))
</details>

<details><summary>13. Compare Flannel with the Amazon VPC CNI.</summary>

Flannel builds an overlay: Pods get addresses from a separate range (`10.244.0.0/16`) and traffic between nodes is
tunnelled with VXLAN. The VPC CNI gives Pods real IP addresses from the VPC subnets, so they are directly routable in
the VPC and visible to security groups and flow logs, at the price of consuming subnet IPs and a per-instance Pod limit.
([docs/06](../docs/06-cni-networking.md), [labs/04](../labs/04-eks-installation.md))
</details>

<details><summary>14. What is the difference between ClusterIP, NodePort, LoadBalancer and Ingress?</summary>

ClusterIP is a virtual address reachable only inside the cluster. NodePort opens one port on every node. LoadBalancer
adds a cloud load balancer in front of a NodePort. Ingress is an HTTP routing rule (host and path to a Service) carried
out by an ingress controller, so many applications can share one entry point on port 80/443.
([labs/03](../labs/03-microk8s-installation.md), [eks/README.md](../eks/README.md))
</details>

## Troubleshooting

<details><summary>15. A node is `NotReady`. What do you do?</summary>

`kubectl describe node` and read the `Ready` condition's message. "Kubelet stopped posting node status" means the
kubelet is down or unreachable: check `systemctl status kubelet` and `journalctl -u kubelet` on the node. A runtime
message means containerd is down: `systemctl is-active containerd`, `crictl ps`. A network-plugin message points at the
CNI. Fix one thing, then verify the node turns Ready. ([troubleshooting 01](../troubleshooting/01-node-not-ready.md),
[07](../troubleshooting/07-container-runtime.md))
</details>

<details><summary>16. A Pod is in `CrashLoopBackOff`. How do you find the cause?</summary>

`kubectl describe pod` shows exit codes, restart counts and events; `kubectl logs --previous` shows what the last crashed
instance printed, which usually names the problem. CrashLoopBackOff is a symptom: the container keeps exiting. Common
causes are bad configuration, missing secrets or files, failing dependencies and wrong commands.
([troubleshooting 06](../troubleshooting/06-core-pods-not-running.md))
</details>

<details><summary>17. A Pod stays `Pending`. What could it be?</summary>

Look at its Events. `Insufficient cpu/memory`: the requests don't fit on any node. `untolerated taint`: the only nodes
with room are tainted. Node selectors or affinity that match no node, or a volume that cannot be bound, are the other
usual causes. Pending Pods have no logs, because no container was started.
([troubleshooting 08](../troubleshooting/08-insufficient-resources.md))
</details>

<details><summary>18. `kubeadm join` hangs. How do you debug it?</summary>

From the bottom up. Network: can the node reach the API server on 6443 (`nc -zv <ip> 6443`)? API server: does
`curl -k https://<ip>:6443/version` answer? Credentials: is the token still in `kubeadm token list` (they expire), and
does the CA hash match? Usually the answer is a firewall or security group, or a stale join command.
([troubleshooting 04](../troubleshooting/04-worker-join-failure.md))
</details>

<details><summary>19. Everything is green, but services on different nodes cannot talk. Where do you look?</summary>

At the Pod network between nodes. Test a request from one node to a Pod IP on another. Then check IP forwarding on the
nodes, the CNI's interfaces and routes, and firewalls or security groups for the overlay traffic (UDP 8472 for Flannel
VXLAN). Health checks that only test locally will not catch this.
([troubleshooting 02](../troubleshooting/02-pod-networking.md))
</details>

## Managed Kubernetes / EKS

<details><summary>20. What does AWS manage in EKS, and what do you manage?</summary>

AWS runs the control plane (API servers, etcd, controllers) across availability zones, including its availability,
patching, backups and the control-plane part of upgrades you trigger. You manage the VPC, the worker nodes or node
groups, IAM access, add-on versions, cluster upgrades, your workloads and their security, and the cost.
([eks/README.md](../eks/README.md), [docs/10](../docs/10-eks-architecture.md))
</details>

<details><summary>21. How do users authenticate to EKS, and why might someone with AWS admin rights see "Unauthorized"?</summary>

kubectl calls `aws eks get-token` with the user's AWS identity; EKS maps that identity to Kubernetes permissions through
access entries (or the older `aws-auth` ConfigMap). An identity without an access entry is refused by Kubernetes even if
its AWS policies allow everything. The console behaves the same way: it reads Pods and nodes through the Kubernetes
API. ([eks Step 8](../eks/README.md))
</details>

<details><summary>22. What costs money in a small EKS lab, and how do you make sure nothing is left?</summary>

The control plane per hour, the EC2 workers, the NAT gateway, public IPv4 addresses, load balancers created by
Services, and EBS volumes. Tag everything, delete LoadBalancer Services before the cluster, delete with the same tool
that created it (`eksctl delete cluster`), then verify by name, by tag and by real state, and compare an inventory of
the region with the one taken before. ([eks/cleanup.md](../eks/cleanup.md))
</details>

## Operations

<details><summary>23. How do you safely remove a node from a cluster?</summary>

`kubectl drain` the node (evicts Pods, respecting disruption budgets, and marks it unschedulable), `kubectl delete node`,
then on the machine `kubeadm reset` and clean the CNI configuration and iptables rules it leaves behind, and only then
remove the machine. ([kubeadm/cleanup.md](../kubeadm/cleanup.md), [labs/01](../labs/01-kubeadm-installation.md))
</details>

<details><summary>24. Why do you hold the Kubernetes packages with `apt-mark hold`?</summary>

So that a routine `apt upgrade` never upgrades kubeadm, kubelet or kubectl behind your back. Cluster upgrades have their
own order: control plane first with `kubeadm upgrade`, then the kubelets node by node, one minor version at a time,
draining each node. ([kubeadm Step 4](../kubeadm/README.md))
</details>

<details><summary>25. How do you verify a new cluster really works?</summary>

Bottom-up: all nodes Ready; system Pods Running; API server healthy (`/readyz`); DNS resolves from inside a Pod; a test
Deployment rolls out; its Service is reachable from outside; a Pod on one node reaches a Pod on another; client and
server versions are within the supported skew. The order points at the broken layer when a check fails.
([docs/11](../docs/11-cluster-verification.md))
</details>
