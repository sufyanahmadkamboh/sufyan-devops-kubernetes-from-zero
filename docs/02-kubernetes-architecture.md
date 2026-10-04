# 02 · Kubernetes architecture

> Time: 25 minutes · Every installation lesson refers back to this page: it is the map of what you install.

A Kubernetes cluster is two kinds of machines: the **control plane**, which decides, and the **worker nodes**, which run
your containers. Everything talks through one door: the **API server**.

```text
                          ┌──────────────────────── CONTROL PLANE ────────────────────────┐
  you                     │                                                                │
  kubectl ── HTTPS :6443 ─┼─► kube-apiserver ◄──────► etcd  (the cluster's database)      │
                          │      ▲    ▲    ▲                                               │
                          │      │    │    └──── kube-controller-manager (reconcile loops) │
                          │      │    └───────── kube-scheduler (which node for each Pod?) │
                          │      └────────────── cloud-controller-manager (cloud only)     │
                          └──────┼─────────────────────────────────────────────────────────┘
                                 │  every node component watches the API server
            ┌────────────────────┼─────────────────────┐
  ┌─────────┴────────── WORKER NODE ──────────┐  ┌──────┴─────────── WORKER NODE ───────────┐
  │ kubelet ── CRI ──► containerd ──► runc    │  │ kubelet ── CRI ──► containerd ──► runc   │
  │ kube-proxy (Service rules: iptables/nft)  │  │ kube-proxy                               │
  │ CNI plugin (Pod network)                  │  │ CNI plugin                               │
  │ [Pod] [Pod] [Pod]                         │  │ [Pod] [Pod]                              │
  └───────────────────────────────────────────┘  └──────────────────────────────────────────┘
```

## Control plane components

| Component | Job | If it is down |
|---|---|---|
| **kube-apiserver** | The front door. Every client (kubectl, kubelets, controllers) reads and writes cluster state only through it. Authenticates, authorises, validates, then stores objects in etcd. Listens on TCP **6443**. | Nothing can be changed or read; running Pods keep running |
| **etcd** | A consistent, distributed key-value store: the **only** place the cluster state lives. Ports 2379–2380. | The API server cannot work. Losing etcd's data = losing the cluster's state: back it up |
| **kube-scheduler** | Watches for Pods with no node, picks a node that fits (free CPU/memory requests, taints, affinity), writes the decision back | New Pods stay `Pending` |
| **kube-controller-manager** | Runs the control loops: Deployment, ReplicaSet, Node (marks nodes NotReady, evicts), Job, ServiceAccount, endpoints… | Nothing reacts: no replacement Pods, no rollouts |
| **cloud-controller-manager** | Only in clouds: talks to the provider's API, for example to create a load balancer for a `type: LoadBalancer` Service | Cloud load balancers and node metadata are not managed |

## Node components

| Component | Job |
|---|---|
| **kubelet** | The agent on every node. Registers the node, watches the API server for Pods assigned to it, asks the runtime to start them, reports their status and the node's health (`Ready`) |
| **container runtime** | Pulls images and runs containers. The kubelet talks to it through the **CRI** (Container Runtime Interface). This course uses **containerd 2.x** ([docs/04](04-container-runtime-and-cri.md)) |
| **kube-proxy** | Turns Services into packet-forwarding rules (iptables or nftables) on every node, so a Service IP reaches a Pod |

## Add-ons every cluster needs

| Add-on | Job |
|---|---|
| **CNI plugin** (Flannel, Calico, Cilium, AWS VPC CNI…) | Gives every Pod an IP and connects Pods across nodes. Without it, nodes stay `NotReady` ([docs/06](06-cni-networking.md)) |
| **CoreDNS** | Cluster DNS: answers names like `web.default.svc.cluster.local` with Service IPs |
| optional: metrics-server, an Ingress controller, a storage driver | `kubectl top`, HTTP routing, persistent volumes |

## What happens when you run `kubectl apply`

Follow one Deployment of 2 nginx Pods through the whole system:

```text
 1. kubectl reads ~/.kube/config, sends the Deployment to the API server over HTTPS
 2. API server: authenticate (certificate/token) → authorise (RBAC) → admission → validate → store in etcd
 3. Deployment controller (controller-manager) sees a new Deployment → creates a ReplicaSet
 4. ReplicaSet controller sees "want 2, have 0" → creates 2 Pod objects (no node yet)
 5. Scheduler sees 2 Pods without a node → scores the nodes → writes nodeName into each Pod
 6. The kubelet on each chosen node sees "a Pod for me" → asks containerd (CRI) to pull the image and start it
 7. The CNI plugin gives the Pod its IP; the kubelet reports the Pod Running
 8. Endpoints of the Service are updated; kube-proxy on every node updates its rules; CoreDNS answers the name
```

Notice: no component tells another what to do directly. Each one **watches** the API server and reacts to changes.
That is why a broken component shows up as "something stops happening" rather than an error message somewhere else.

## Where the components live, per installation method

| | kubeadm ([lesson](../kubeadm/README.md)) | Minikube ([lesson](../minikube/README.md)) | MicroK8s ([lesson](../microk8s/README.md)) | Amazon EKS ([lesson](../eks/README.md)) |
|---|---|---|---|---|
| API server, scheduler, controller manager | **static Pods** started by the kubelet from `/etc/kubernetes/manifests` | static Pods inside one **container** (the "node") on your Docker engine | one process, **kubelite**, run by the snap as a systemd service | run by **AWS**, on machines you never see |
| Cluster datastore | etcd (static Pod) | etcd inside the node container | **dqlite** (distributed SQLite) | etcd run by AWS |
| kubelet + runtime | systemd service + containerd on each VM | inside the node container | inside kubelite + containerd from the snap | on your EC2 worker nodes (Amazon Linux 2023, containerd) |
| CNI | you install it (Flannel) | built in | Calico, preinstalled | Amazon VPC CNI (`aws-node` Pods) |
| Who fixes the control plane | you | you (`minikube delete` and start) | you | AWS |

## Check yourself

<details><summary>1. Which component is the only one that talks to etcd?</summary>

The kube-apiserver. Every other component reads and writes state through the API server.
</details>

<details><summary>2. A new Pod stays Pending and its events say nothing was scheduled. Which component made that decision?</summary>

The kube-scheduler: it found no node that fits (for example `Insufficient cpu`), see troubleshooting 08.
</details>

<details><summary>3. What does the kubelet do, and what does it not do?</summary>

It registers the node, watches for Pods assigned to it, has the container runtime start them and reports status. It
does not decide where Pods run, and it does not run containers itself (the runtime does).
</details>

<details><summary>4. Why are there no kube-apiserver Pods on MicroK8s or EKS?</summary>

On MicroK8s the control plane runs inside the kubelite service; on EKS AWS runs it outside your account. Only kubeadm
and Minikube run the control plane as (static) Pods you can see.
</details>

<details><summary>5. Which add-on must be installed before a kubeadm node becomes Ready?</summary>

A CNI plugin. Without a Pod network the kubelet reports the node NotReady.
</details>

Next: [03 · Installation prerequisites](03-installation-prerequisites.md)
