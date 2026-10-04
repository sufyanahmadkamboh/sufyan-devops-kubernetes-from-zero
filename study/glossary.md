# Glossary

Every term used in this course, in plain words. The link points to where it is explained or used.

| Term | Meaning |
|---|---|
| **Access entry** | An EKS object that gives an AWS identity (user or role) permissions inside the Kubernetes cluster. AWS permissions alone are not enough. [docs/10](../docs/10-eks-architecture.md) |
| **Add-on** | An optional, pre-packaged component (DNS, metrics, ingress, storage). Minikube, MicroK8s and EKS all have their own add-on mechanism. [docs/08](../docs/08-minikube-internals.md) |
| **admin.conf** | The kubeconfig kubeadm writes with cluster-admin rights. Treat it like a root password. [docs/05](../docs/05-kubeadm-installation.md) |
| **Allocatable** | The CPU and memory of a node that Pods may request, after reserving some for the system. [troubleshooting 08](../troubleshooting/08-insufficient-resources.md) |
| **Amazon EKS** | AWS's managed Kubernetes: AWS runs the control plane, you run the nodes and workloads. [eks/README.md](../eks/README.md) |
| **API server (kube-apiserver)** | The front door of the cluster. Every component and every kubectl command talks to it, and only it talks to etcd. [docs/02](../docs/02-kubernetes-architecture.md) |
| **Availability zone (AZ)** | One or more separate data centres inside an AWS region. Spreading nodes over AZs survives the loss of one. [docs/10](../docs/10-eks-architecture.md) |
| **aws-node** | The DaemonSet of the Amazon VPC CNI on EKS nodes. [labs/04](../labs/04-eks-installation.md) |
| **Bootstrap token** | A short-lived token that lets a new node authenticate when it joins with `kubeadm join`. Expires after 24 hours by default. [troubleshooting 04](../troubleshooting/04-worker-join-failure.md) |
| **br_netfilter** | A kernel module that makes bridged traffic visible to iptables, where Service rules live. [docs/03](../docs/03-installation-prerequisites.md) |
| **CA certificate hash** | A fingerprint of the cluster's certificate authority. The joining node uses it to verify it talks to the real control plane. [docs/05](../docs/05-kubeadm-installation.md) |
| **Calico** | A CNI plugin with network policy support; the default CNI of MicroK8s. [docs/06](../docs/06-cni-networking.md) |
| **cgroup / cgroup driver** | The Linux feature that limits and accounts for CPU and memory. The kubelet and the runtime must use the same driver (systemd here). [docs/04](../docs/04-container-runtime-and-cri.md) |
| **Channel (snap)** | A version track of a snap package, like `1.36/stable` for MicroK8s. [docs/09](../docs/09-microk8s-internals.md) |
| **CloudFormation stack** | A group of AWS resources created and deleted together from a template. eksctl creates one for the cluster and one per node group. [eks/README.md](../eks/README.md) |
| **Cluster** | A set of nodes managed by one control plane. [docs/01](../docs/01-what-is-kubernetes.md) |
| **CNI (Container Network Interface)** | The standard for network plugins that give Pods their network. Without one, nodes stay `NotReady`. [docs/06](../docs/06-cni-networking.md) |
| **ConfigMap** | A Kubernetes object holding configuration data, such as CoreDNS's Corefile. [troubleshooting 06](../troubleshooting/06-core-pods-not-running.md) |
| **containerd** | The container runtime used in this course. The kubelet talks to it through the CRI. [docs/04](../docs/04-container-runtime-and-cri.md) |
| **Context** | A named entry in a kubeconfig: which cluster, which user, which namespace. [troubleshooting 05](../troubleshooting/05-kubectl-connection.md) |
| **Control plane** | The components that make decisions for the cluster: API server, etcd, scheduler, controller manager. [docs/02](../docs/02-kubernetes-architecture.md) |
| **Controller manager (kube-controller-manager)** | Runs the control loops that make actual state match desired state (Deployments, ReplicaSets, nodes, ...). [docs/02](../docs/02-kubernetes-architecture.md) |
| **CoreDNS** | The cluster DNS server that lets Pods find Services by name. [troubleshooting 06](../troubleshooting/06-core-pods-not-running.md) |
| **CrashLoopBackOff** | A Pod status: the container keeps exiting and Kubernetes restarts it with growing delays. The cause is in the logs. [troubleshooting 06](../troubleshooting/06-core-pods-not-running.md) |
| **CRI (Container Runtime Interface)** | The API the kubelet uses to talk to a container runtime. [docs/04](../docs/04-container-runtime-and-cri.md) |
| **crictl** | The command-line client for the CRI; the way to check a runtime as the kubelet sees it. [troubleshooting 03](../troubleshooting/03-kubeadm-init-failure.md) |
| **DaemonSet** | A workload that runs one Pod on every (matching) node, used by CNI plugins and kube-proxy. [docs/06](../docs/06-cni-networking.md) |
| **Deployment** | A workload that keeps a number of identical Pods running and replaces them during updates. [examples/nginx](../examples/nginx/README.md) |
| **Desired state** | What you declared in Kubernetes objects. Controllers keep reality matching it. [docs/01](../docs/01-what-is-kubernetes.md) |
| **dqlite** | The distributed SQLite datastore MicroK8s uses instead of etcd. [docs/09](../docs/09-microk8s-internals.md) |
| **Drain** | Evicting all Pods from a node before maintenance or removal (`kubectl drain`). [kubeadm/cleanup.md](../kubeadm/cleanup.md) |
| **Driver (Minikube)** | What Minikube runs its node in: a Docker container, a VM (Hyper-V, KVM, QEMU) or Podman. [docs/08](../docs/08-minikube-internals.md) |
| **eksctl** | The official command-line tool that creates and deletes EKS clusters from a YAML file. [eks/README.md](../eks/README.md) |
| **Endpoint (Service)** | The list of Pod IPs a Service currently sends traffic to. Empty means no matching Ready Pods. [examples/nginx](../examples/nginx/README.md) |
| **etcd** | The key-value store holding the whole cluster state. Back it up on self-managed clusters. [docs/02](../docs/02-kubernetes-architecture.md) |
| **Events** | Short records of what happened to an object (scheduled, pulled, failed, ...). Shown at the end of `kubectl describe`. [troubleshooting 08](../troubleshooting/08-insufficient-resources.md) |
| **Flannel** | A simple CNI plugin that connects nodes with a VXLAN overlay; used in the kubeadm lesson. [docs/06](../docs/06-cni-networking.md) |
| **Ingress / ingress controller** | An Ingress is an HTTP routing rule (host and path to a Service); the controller is the program that carries it out. [labs/03](../labs/03-microk8s-installation.md) |
| **ip_forward** | The Linux setting that lets a machine route packets. Without it, Pod traffic between nodes stops. [troubleshooting 02](../troubleshooting/02-pod-networking.md) |
| **kubeadm** | The official tool that turns prepared Linux machines into a cluster (`init`, `join`, `reset`, `upgrade`). [kubeadm/README.md](../kubeadm/README.md) |
| **kubeconfig** | The file that tells kubectl where the API server is and how to authenticate. Default `~/.kube/config`. [troubleshooting 05](../troubleshooting/05-kubectl-connection.md) |
| **kubectl** | The command-line client for the Kubernetes API. [docs/02](../docs/02-kubernetes-architecture.md) |
| **kubelet** | The agent on every node that starts Pods through the runtime and reports their status. [docs/02](../docs/02-kubernetes-architecture.md) |
| **kubelite** | MicroK8s's single process that contains the API server, scheduler, controller manager, kubelet and proxy. [docs/09](../docs/09-microk8s-internals.md) |
| **kube-proxy** | Runs on every node and programs the rules that send Service traffic to Pods. [docs/02](../docs/02-kubernetes-architecture.md) |
| **Label / selector** | Key-value tags on objects, and the queries that pick objects by them. Services find their Pods this way. [examples/nginx](../examples/nginx/README.md) |
| **Liveness / readiness probe** | Health checks: liveness restarts a stuck container, readiness decides whether a Pod gets traffic. [examples/nginx](../examples/nginx/README.md) |
| **LoadBalancer (Service type)** | A NodePort Service plus a cloud load balancer in front of it. [eks/README.md](../eks/README.md) |
| **Managed node group** | EKS-managed EC2 workers in an Auto Scaling group that join the cluster on their own. [docs/10](../docs/10-eks-architecture.md) |
| **Minikube** | A tool that runs a complete local cluster, usually in one Docker container. [minikube/README.md](../minikube/README.md) |
| **MicroK8s** | Kubernetes packaged as one snap, for single machines and edge devices. [microk8s/README.md](../microk8s/README.md) |
| **Namespace** | A named section of a cluster that groups objects (`kube-system`, `default`, ...). [docs/02](../docs/02-kubernetes-architecture.md) |
| **NAT gateway** | An AWS service that lets machines in private subnets reach the internet. Billed per hour, a classic forgotten cost. [eks/README.md](../eks/README.md) |
| **Node** | A machine (VM, server, container in Minikube) that runs Pods. [docs/02](../docs/02-kubernetes-architecture.md) |
| **NodePort** | A Service type that opens the same port (30000–32767) on every node. [kubeadm/README.md](../kubeadm/README.md) |
| **NotReady** | A node status: the kubelet reports a problem (no CNI, runtime down) or stopped reporting at all. [troubleshooting 01](../troubleshooting/01-node-not-ready.md) |
| **overlay (module)** | The filesystem driver containerd uses to stack image layers. [docs/03](../docs/03-installation-prerequisites.md) |
| **Pending** | A Pod status: not yet placed on a node, or its containers not created yet. The Events say why. [troubleshooting 08](../troubleshooting/08-insufficient-resources.md) |
| **Pod** | The smallest unit Kubernetes runs: one or more containers sharing a network address. [docs/01](../docs/01-what-is-kubernetes.md) |
| **Pod network CIDR** | The address range for Pod IPs, `10.244.0.0/16` for Flannel in the kubeadm lesson. [docs/06](../docs/06-cni-networking.md) |
| **Preflight checks** | kubeadm's checks before it changes anything (CPUs, memory, swap, ports, runtime). [troubleshooting 03](../troubleshooting/03-kubeadm-init-failure.md) |
| **Profile (Minikube)** | A separately named Minikube cluster with its own kubectl context. [labs/02](../labs/02-minikube-installation.md) |
| **Requests and limits** | Requests are what the scheduler reserves for a container; limits are the hard maximum. [troubleshooting 08](../troubleshooting/08-insufficient-resources.md) |
| **Rolling update** | Replacing Pods gradually, keeping the old ones until the new ones are Ready. [troubleshooting 06](../troubleshooting/06-core-pods-not-running.md) |
| **runc** | The low-level tool containerd uses to actually create containers. [docs/04](../docs/04-container-runtime-and-cri.md) |
| **Scheduler (kube-scheduler)** | Chooses a node for each new Pod, based on requests, taints, affinity and more. [docs/02](../docs/02-kubernetes-architecture.md) |
| **Service** | A stable virtual address and DNS name in front of a changing set of Pods. [docs/02](../docs/02-kubernetes-architecture.md) |
| **Snap** | Ubuntu's package format with versioned channels and automatic refreshes; MicroK8s ships as one. [docs/09](../docs/09-microk8s-internals.md) |
| **Static Pod** | A Pod the kubelet starts from a file on disk; kubeadm runs the control plane this way. [docs/05](../docs/05-kubeadm-installation.md) |
| **Swap** | Disk used as extra memory. The kubelet refuses to run with it by default. [docs/03](../docs/03-installation-prerequisites.md) |
| **Taint / toleration** | A taint keeps Pods off a node unless they carry a matching toleration. The control plane is tainted. [kubeadm/README.md](../kubeadm/README.md) |
| **Version skew** | The supported difference between component versions, for example kubectl one minor version newer or older than the API server. [labs/02](../labs/02-minikube-installation.md) |
| **VPC / subnet** | Your private network in AWS, divided into subnets per availability zone. [docs/10](../docs/10-eks-architecture.md) |
| **VPC CNI (Amazon)** | The EKS network plugin that gives Pods real IP addresses from the VPC's subnets. [docs/06](../docs/06-cni-networking.md) |
| **VXLAN** | A way to tunnel Layer 2 traffic over UDP; Flannel uses it to connect Pod networks across nodes. [docs/06](../docs/06-cni-networking.md) |
