# 10 · Amazon EKS architecture

> Time: 20 minutes · Read it before the [EKS lesson](../eks/README.md).

On kubeadm, Minikube and MicroK8s **you** run the control plane. On Amazon EKS (Elastic Kubernetes Service), AWS runs
it for you, and you only bring the worker nodes (or let AWS run those too). This chapter shows where every piece
lives, who pays for what, and how identity works, because that is where most EKS surprises come from.

## Two accounts: AWS's and yours

```text
 ┌──────────────────────── AWS-managed account (you never see it) ────────────────────────┐
 │  EKS control plane for "k8s-from-zero"                                                   │
 │   kube-apiserver ×2+ and etcd ×3, spread over 3 availability zones, behind a load balancer │
 │   upgraded, backed up, scaled and patched by AWS                                         │
 └──────────────────────────────────┬──────────────────────────────────────────────────────┘
                                    │  cross-account ENIs (network interfaces) placed in YOUR subnets
 ┌──────────────────────────────────▼──────── your AWS account, eu-central-1 ──────────────┐
 │  VPC 10.50.0.0/16 (created by eksctl from eks/cluster.yaml)                               │
 │                                                                                           │
 │   public subnets (one per AZ)               private subnets (one per AZ)                  │
 │   ┌──────────────────────────┐              ┌──────────────────────────────────────────┐  │
 │   │ NAT gateway (single)      │◀── egress ──│ node 1 (t3.medium, AL2023)                │  │
 │   │ Elastic IP                │              │ node 2 (t3.medium, AL2023)                │  │
 │   │ internet-facing load      │── traffic ─▶│ Pods get real VPC IPs (VPC CNI)           │  │
 │   │ balancer for Service web  │              │ control-plane ENIs                        │  │
 │   └────────────┬─────────────┘              └──────────────────────────────────────────┘  │
 │                │ internet gateway                                                          │
 └────────────────┼──────────────────────────────────────────────────────────────────────────┘
                  ▼
              Internet  ← your kubectl talks to the public API endpoint (https://<id>.gr7.eu-central-1.eks.amazonaws.com)
```

Key points:

- The control plane is **multi-AZ** and **not visible as machines**: `kubectl get nodes` lists only your workers.
  You cannot SSH into it, and you do not see `kube-apiserver` or `etcd` Pods in `kube-system`.
- AWS places **ENIs** (elastic network interfaces) of the control plane into your subnets, so the API server can reach
  the kubelets (for `kubectl logs`, `exec`, webhooks) inside your VPC.
- Our `cluster.yaml` puts the nodes in **private subnets** (`privateNetworking: true`): they have no public IP and reach
  the internet (image pulls, AWS APIs) through the single NAT gateway. Production uses one NAT gateway per AZ.

## Endpoint access

| Setting | Who can reach the API server | Our lab |
|---|---|---|
| public | anyone on the internet (still needs valid AWS credentials + Kubernetes permission); can be limited to CIDRs | on, so kubectl works from your laptop |
| private | only from inside the VPC (and connected networks) | on, so node traffic stays inside the VPC |
| public + private | both | ✔ |

## Where the worker nodes come from

| Option | What you manage | When |
|---|---|---|
| **Managed node group** (our lab: `workers`) | instance type, size, scaling limits; AWS creates the Auto Scaling group + launch template, and handles draining during updates | the usual default |
| **EKS Auto Mode** | almost nothing: AWS picks, launches, patches and replaces nodes (Karpenter-based), plus storage and load balancing | teams who want the least operations work; costs a fee on top of EC2 |
| **Fargate** | nothing at node level: each Pod runs in its own AWS-managed micro-VM | small or bursty workloads; no DaemonSets |
| **Self-managed nodes** | everything: your own Auto Scaling group, AMI, bootstrap, upgrades | special AMIs or OS requirements |

Our nodes run **Amazon Linux 2023** (the EKS-optimised AMI) with **containerd** and the kubelet, exactly the
components from [02 · Architecture](02-kubernetes-architecture.md). In the lesson, `kubectl get nodes -o wide` shows the
OS image and `containerd://2.x`.

## Pod networking: the Amazon VPC CNI

EKS uses the **VPC CNI** (`aws-node` DaemonSet) by default. Unlike Flannel's overlay ([06 · CNI](06-cni-networking.md)),
every Pod gets a **real IP address from your VPC subnet** (in the lesson, Pods have `10.50.x.x` addresses, like the nodes).
Consequences:

- no overlay: Pods are directly routable inside the VPC, and security groups and VPC flow logs see Pod IPs;
- the number of Pods per node is limited by how many ENIs and IPs the instance type supports;
- subnets must be big enough for nodes **and** Pods (a /16 VPC leaves plenty of room).

## Identity: three different questions

```text
 1. What may the CONTROL PLANE do in my account?   → cluster IAM role   (eksctl-k8s-from-zero-cluster-ServiceRole-…)
 2. What may the NODES do?                          → node IAM role      (pull images from ECR, attach ENIs, join the cluster)
 3. Which HUMANS / CI may use kubectl?              → access entries     (IAM principal → Kubernetes permissions)
 4. What may a POD do in AWS?                       → EKS Pod Identity or IRSA (an IAM role for one service account)
```

**Access entries vs aws-auth.** Kubernetes itself knows nothing about IAM. EKS maps IAM identities to Kubernetes
users:

| Mode | How | Status |
|---|---|---|
| `aws-auth` ConfigMap | a YAML list in `kube-system` mapping IAM ARNs to groups | legacy; one typo can lock everybody out |
| **access entries** (`authenticationMode: API`, our lab) | managed through the EKS API / console / eksctl, with AWS-managed access policies (e.g. `AmazonEKSClusterAdminPolicy`) | current recommendation |

The IAM identity that creates the cluster gets an admin access entry automatically. Anyone else, including a console
user, needs an access entry before they can see Kubernetes objects. You can see this in the lesson's console tour:
the read-only console user sees the cluster's AWS settings, but the **Resources** and **Compute → Nodes** views say
"Unauthorized", because that user has no access entry.

kubectl authenticates with your **AWS** credentials: the kubeconfig entry runs `aws eks get-token` (or `eksctl`) on
every request and sends a short-lived token.

## Add-ons

EKS add-ons are AWS-managed versions of cluster components that AWS keeps compatible with the Kubernetes version:
`vpc-cni`, `kube-proxy`, `coredns` (installed by default) and optional ones such as `metrics-server`,
`eks-pod-identity-agent`, `aws-ebs-csi-driver`. eksctl v0.231.0 also installed `metrics-server` in the lesson's run.

## What eksctl builds: CloudFormation stacks

eksctl does not call the EKS API piece by piece; it writes **CloudFormation** templates and lets CloudFormation create
(and later delete) everything as a unit:

| Stack | Contains |
|---|---|
| `eksctl-k8s-from-zero-cluster` | VPC, subnets, route tables, internet gateway, NAT gateway + Elastic IP, security groups, cluster IAM role, the EKS cluster |
| `eksctl-k8s-from-zero-nodegroup-workers` | node IAM role, launch template, managed node group (→ Auto Scaling group → EC2 instances + EBS volumes) |

Two things are **not** in these stacks: load balancers created by `Service type: LoadBalancer` (created by Kubernetes)
and volumes created by PersistentVolumeClaims. Delete those from Kubernetes **before** deleting the cluster
([12 · Cleanup](12-cleanup-and-reset.md)).

## Support periods and versions

EKS 1.37 has **standard support** for about 14 months after its release on EKS, then optional **extended support** for
another 12 months at a much higher control-plane price. The cluster's *upgrade policy* decides what happens at the end
of standard support: stay on extended support (and pay for it) or be upgraded automatically. Check this setting on
every cluster you own (console → cluster → Overview → Kubernetes version settings).

## What it costs

| Component | Billed | Note for our lab |
|---|---|---|
| EKS control plane | per cluster per hour (standard support: $0.10/h at the time of writing) | the same for a tiny or a huge cluster |
| EC2 worker nodes | per instance per second | 2 × t3.medium |
| NAT gateway | per hour + per GB processed | runs as long as the VPC exists |
| Public IPv4 addresses | per address per hour | NAT gateway EIP, load balancer |
| Load balancer | per hour + per capacity unit | only while Service `web` exists |
| EBS volumes | per GB-month | 2 × 20 GB gp3 |
| Data transfer | per GB out to the internet / across AZs | small for a lab |

The estimate in `eks/cluster.yaml` is **about $0.25–0.30 per hour** for the whole lab in eu-central-1. Prices change
and differ by region: always check the [AWS pricing pages](https://aws.amazon.com/eks/pricing/) and set an AWS Budget
alarm before you create anything.

## Check yourself

<details><summary>Why does `kubectl get nodes` on EKS show only your two workers?</summary>

The control plane runs in an AWS-managed account, not as nodes in your cluster. It reaches your VPC through ENIs.
</details>

<details><summary>What is the practical difference between Pod IPs on EKS (VPC CNI) and on the kubeadm lab (Flannel)?</summary>

On EKS, Pods get real IPs from the VPC subnets (directly routable, limited by ENI/IP capacity per instance). Flannel
gives Pods addresses from a separate overlay range (10.244.0.0/16) and encapsulates traffic between nodes.
</details>

<details><summary>A colleague can see your cluster in the console but every Kubernetes view says "Unauthorized". What is missing?</summary>

An EKS access entry (with an access policy) for their IAM principal. IAM permissions to the EKS API alone do not give
Kubernetes permissions.
</details>

<details><summary>Which resources do NOT disappear when CloudFormation deletes the eksctl stacks, and why?</summary>

Load balancers from `Service type: LoadBalancer` and volumes from PersistentVolumeClaims. Kubernetes controllers created
them through AWS APIs, so they are not part of the stacks. Delete them from Kubernetes first.
</details>

<details><summary>Why did we put the nodes in private subnets, and what do they need to pull images?</summary>

So they have no public IP and cannot be reached from the internet. They need outbound access, provided here by the
NAT gateway (or VPC endpoints for ECR/S3 in a locked-down setup).
</details>

Next: [11 · Cluster verification checklist](11-cluster-verification.md)
