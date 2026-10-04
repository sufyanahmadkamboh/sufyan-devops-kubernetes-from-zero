# Capstone · prove it

> After all ten levels of the [roadmap](../README.md). Time: 60–90 minutes. Part A without notes, Part B with a
> terminal.

## Part A · 15 questions

Answer in your own words first. Then open the answer and compare.

**1. A colleague says "Kubernetes runs my containers". Which component actually starts a container on a node, and
which components are involved between `kubectl apply` and the running container?**

<details><summary>Answer</summary>

kubectl sends the object to the **API server**, which validates it and stores it in **etcd**. The **controller
manager** (Deployment and ReplicaSet controllers) creates Pod objects; the **scheduler** assigns each Pod to a node; the
**kubelet** on that node sees the Pod and asks the **container runtime** (containerd, through the CRI) to pull the
image and start the container, which runc finally creates. See [docs/02](../docs/02-kubernetes-architecture.md).
</details>

**2. Why must swap be handled, and why are `br_netfilter` and `net.ipv4.ip_forward` needed?**

<details><summary>Answer</summary>

The kubelet's resource accounting assumes memory limits are real; by default it refuses to start with swap on (newer
versions support swap only when explicitly configured). `br_netfilter` + `bridge-nf-call-iptables` make traffic that
crosses a Linux bridge (Pod to Pod on a node) go through iptables, where kube-proxy's Service rules live.
`ip_forward` lets the node route packets between Pods, other nodes and the outside: without it cross-node Pod traffic
dies, which is exactly [troubleshooting 02](../troubleshooting/02-pod-networking.md).
</details>

**3. What is the CRI, and why did "Docker support" disappear from Kubernetes in 1.24?**

<details><summary>Answer</summary>

The Container Runtime Interface is the gRPC API the kubelet uses to talk to a runtime. Docker Engine never implemented
it; Kubernetes carried an adapter (dockershim), which was removed in 1.24. Runtimes that implement CRI (containerd,
CRI-O) are used directly. Images built with Docker still run everywhere: they are standard OCI images.
</details>

**4. containerd is `active`, but `kubeadm init` fails its preflight with a runtime error. What do you check?**

<details><summary>Answer</summary>

Whether the **CRI plugin** answers: `sudo crictl --runtime-endpoint unix:///run/containerd/containerd.sock version`.
The `containerd.io` package config disables it (`disabled_plugins = ["cri"]`); regenerate the config with
`containerd config default`, set `SystemdCgroup = true`, restart. [Troubleshooting 03](../troubleshooting/03-kubeadm-init-failure.md).
</details>

**5. Why is the control plane `NotReady` right after `kubeadm init`, and what fixes it?**

<details><summary>Answer</summary>

No CNI plugin is installed yet: the kubelet reports `NetworkReady=false reason:NetworkPluginNotReady ... cni plugin not
initialized`. Installing a CNI (Flannel in the lesson, matching `--pod-network-cidr=10.244.0.0/16`) makes it Ready.
</details>

**6. A worker's join hangs at discovery. Name three causes and the command that tells them apart.**

<details><summary>Answer</summary>

Port 6443 blocked (firewall / security group) → `nc -zv <cp-ip> 6443` fails; wrong API server address → same; expired
or wrong token → network fine, `curl -k https://<cp-ip>:6443/version` answers, but the token is missing from `kubeadm
token list`. A wrong CA hash is reported explicitly by the join. [Troubleshooting 04](../troubleshooting/04-worker-join-failure.md).
</details>

**7. `kubectl get nodes` says `The connection to the server localhost:8080 was refused`. What does that tell you?**

<details><summary>Answer</summary>

kubectl found **no kubeconfig** at all and fell back to its default. Check `$KUBECONFIG`, `~/.kube/config`, and
`kubectl config current-context`. [Troubleshooting 05](../troubleshooting/05-kubectl-connection.md).
</details>

**8. A node is `NotReady`. How do you tell "the kubelet is dead" from "the runtime is dead"?**

<details><summary>Answer</summary>

`kubectl describe node` → Conditions. Kubelet gone: `Kubelet stopped posting node status` (no fresh heartbeats, node
gets the `unreachable` taint). Runtime gone: the kubelet still reports, with a container-runtime message; on the node
`systemctl is-active containerd` is inactive and `crictl ps` cannot connect. [01](../troubleshooting/01-node-not-ready.md),
[07](../troubleshooting/07-container-runtime.md).
</details>

**9. CoreDNS Pods are in `CrashLoopBackOff`. What is your sequence of commands?**

<details><summary>Answer</summary>

`kubectl get pods -n kube-system -l k8s-app=kube-dns` → `kubectl describe pod` (exit code, back-off events) →
`kubectl logs --previous` (the crash reason, e.g. an unknown Corefile directive) → fix the ConfigMap (from a backup)
→ `kubectl rollout restart` + `rollout status` → test DNS from a Pod with `nslookup`. [Troubleshooting 06](../troubleshooting/06-core-pods-not-running.md).
</details>

**10. A Pod stays `Pending`. Where is the reason, and what does `Insufficient cpu` mean exactly?**

<details><summary>Answer</summary>

In the Pod's **Events** (`kubectl describe pod`), written by the scheduler. `Insufficient cpu`: on no node does
allocatable CPU minus the **requests** of Pods already there leave room for this Pod's request. Real usage does not
count. Fix the request or add capacity. [Troubleshooting 08](../troubleshooting/08-insufficient-resources.md).
</details>

**11. What is the difference between Minikube, MicroK8s and kubeadm in where the control plane runs?**

<details><summary>Answer</summary>

kubeadm: static Pods (API server, etcd, scheduler, controller manager) managed by the kubelet on the control-plane
machine. Minikube: a whole node (with kubeadm inside) running as a Docker container (or VM) on your computer.
MicroK8s: all components in one process (`kubelite`) installed by a snap, with dqlite instead of etcd.
</details>

**12. On EKS, what do you manage and what does AWS manage?**

<details><summary>Answer</summary>

AWS: the control plane (API servers, etcd) across availability zones, its scaling, patching, backups and certificates.
You: the VPC, node groups (instance type, size, AMI updates), add-on versions, IAM (cluster and node roles, access
entries), workloads, and cluster version upgrades (which you trigger). [docs/10](../docs/10-eks-architecture.md).
</details>

**13. Why must LoadBalancer Services be deleted before `eksctl delete cluster`?**

<details><summary>Answer</summary>

The load balancer was created by Kubernetes (the cloud controller), not by eksctl's CloudFormation stacks. If the
cluster disappears first, nothing deletes the load balancer: it keeps costing money, and its network interfaces and
security group block the deletion of the VPC. [eks/cleanup.md](../eks/cleanup.md).
</details>

**14. What does `kubeadm reset` not clean up?**

<details><summary>Answer</summary>

The CNI configuration in `/etc/cni/net.d`, iptables/IPVS rules, and kubeconfig files in users' home directories (e.g.
`~/.kube/config`). It also does not uninstall packages or containerd. [kubeadm/cleanup.md](../kubeadm/cleanup.md),
[docs/12](../docs/12-cleanup-and-reset.md).
</details>

**15. Your Pods on EKS have IPs like `10.50.159.242`, on kubeadm `10.244.1.5`. Why the difference, and what is one
consequence?**

<details><summary>Answer</summary>

The Amazon VPC CNI gives Pods real VPC addresses from the subnets; Flannel gives them addresses from its own overlay
range (`10.244.0.0/16`) and encapsulates traffic in VXLAN. Consequences: on EKS, Pods are directly reachable inside
the VPC and visible to security groups and flow logs, but they consume subnet IPs and the number of Pods per node is
limited by the instance's network interfaces. [docs/06](../docs/06-cni-networking.md).
</details>

## Part B · Scenario: the Monday morning cluster

You join a team on Monday. Their **kubeadm** test cluster (`k8s-cp` + `k8s-worker`) "stopped working over the weekend".
Rebuild that situation from the lessons, then fix it as if you did not know what was done.

### Set it up (on your computer, with the kubeadm cluster from the lesson running)

Ask a friend to run these, or run them and then wait a day before you start:

<!-- test: timeout=120 -->
```bash
# three faults at once
multipass exec k8s-worker -- sudo systemctl stop containerd
multipass exec k8s-worker -- sudo sysctl -w net.ipv4.ip_forward=0
multipass exec k8s-cp -- bash -c 'cp ~/.kube/config ~/.kube/config.bak && sed -i "s#server: https://.*:6443#server: https://10.255.255.1:6443#" ~/.kube/config'
```

### Your task

1. Find **every** fault, starting from what a user would see (`kubectl get nodes` on the control plane).
2. For each fault, write down: symptom → command that proves the cause → root cause → fix → verification.
3. Restore the cluster to a fully verified state with the [verification checklist](../docs/11-cluster-verification.md):
   nodes Ready, system Pods Running, DNS works, the test app answers through its NodePort **and** a Pod on one node can
   reach a Pod on the other.
4. Write a short incident note (5–10 lines): what broke, impact, how you found it, how you fixed it, how to prevent it.

### Hints

- Fix the layer that hides the others first: you cannot investigate nodes while kubectl cannot reach the API.
- After the node is `Ready`, everything may *look* fine. Test traffic across nodes.

<details>
<summary>Solution outline</summary>

1. `kubectl get nodes` → `i/o timeout` to `10.255.255.1`: wrong server in `~/.kube/config` (`kubectl config view
   --minify`). Fix: restore `config.bak` or copy `/etc/kubernetes/admin.conf` again.
2. `kubectl get nodes` → `k8s-worker NotReady`; `describe node` shows a container-runtime message; on the worker
   `systemctl is-active containerd` → inactive. Fix: `sudo systemctl start containerd`; wait for Ready.
3. Checklist: NodePort on the worker answers locally, but `curl` from the control plane to a Pod IP on the worker times
   out; on the worker `sysctl net.ipv4.ip_forward` → 0. Fix: `sudo sysctl --system` (the value in
   `/etc/sysctl.d/k8s.conf` is 1), then re-run the full checklist.

<!-- test-run on=k8s-cp: ! kubectl get nodes --request-timeout=5s -->
<!-- test-run on=k8s-cp: cp ~/.kube/config.bak ~/.kube/config && rm ~/.kube/config.bak -->
<!-- test-run on=k8s-worker: sudo systemctl start containerd -->
<!-- test-run on=k8s-cp: kubectl wait --for=condition=Ready node/k8s-worker --timeout=300s -->
<!-- test-run on=k8s-worker: test "$(sysctl -n net.ipv4.ip_forward)" = 0 && sudo sysctl --system > /dev/null && test "$(sysctl -n net.ipv4.ip_forward)" = 1 -->
<!-- test-run on=k8s-cp: for i in $(seq 60); do kubectl get pods -A --no-headers | awk '$4 != "Running" && $4 != "Completed" {bad=1} END {exit bad}' && exit 0; sleep 3; done; exit 1 -->

Prevention: configuration management for kubeconfig and sysctls, node monitoring (NotReady alerts), and an automated
smoke test that includes cross-node traffic.
</details>
