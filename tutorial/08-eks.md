# 08 · Amazon EKS

> Goal: understand a managed cluster, create one on AWS from a single file, see the same thing in the console, prove it
> works, and delete everything with proof. Time: about 90 minutes. Level 8 of the [roadmap](../README.md#4-the-roadmap).

```text
⚠️ THE EKS LESSON CREATES AWS RESOURCES THAT COST MONEY (about $0.25-0.30 per hour).
You can do this whole chapter as a read-along: every output quoted here comes from the real recorded run.
```

## Before you start

Decide which way you do this chapter:

| You have | Do |
|---|---|
| an AWS account you may spend a few dollars on, and permission to create EKS, EC2, VPC, IAM and CloudFormation | the full lesson, then the cleanup **the same day** |
| no such account | read along with the real outputs and screenshots, then do lab 04, which needs no account |

If you do it for real: set an AWS Budget alert first, and pick one region you will use for nothing else in this lab.

## The walk

### 1. Read docs/10 · Amazon EKS architecture

Open [docs/10](../docs/10-eks-architecture.md). The key change compared with everything so far: **you no longer see the
control plane.** It runs in an AWS-owned account across several availability zones. You get an API endpoint, and your
nodes attach to it.

```text
        AWS-managed (invisible)                      your AWS account
  ┌─────────────────────────────┐        ┌──────────────────────────────────────────────┐
  │ API servers, etcd,          │◄─HTTPS─┤ VPC 10.50.0.0/16: public + private subnets,  │
  │ scheduler, controllers      │        │ NAT gateway, node group "workers" (2 x EC2), │
  │ multi-AZ, patched, backed up│        │ load balancers created by your Services      │
  └─────────────────────────────┘        └──────────────────────────────────────────────┘
```

### 2. Lesson Steps 1–3: tools, identity, inventory, the cluster file

Open [eks/README.md](../eks/README.md) and work through **Steps 1–3**.

The two habits this lesson teaches before anything is created:

1. **Who am I, and where?** `aws sts get-caller-identity` and the region. The real run printed an ARN (masked here):

   ```text
   arn:aws:iam::<account-id>:user/<iam-user>
   ```

2. **Inventory before you start.** `eks/scripts/inventory.sh` counts what already exists in the region, so later you
   can prove you removed only what you created:

   ```text
   Region: eu-central-1
   EKS clusters:          0
   VPCs:                  1
   NAT gateways (active): 0
   Elastic IPs:           0
   Load balancers:        0
   EC2 instances (on):    0
   CloudFormation stacks: 1
   ```

   The one VPC and one stack were already there and are not ours. A shared account always has things you must not
   touch.

Read [eks/cluster.yaml](../eks/cluster.yaml) line by line with the settings table of Step 3. One file describes the
region, the version, the tags, a new VPC with one NAT gateway, the access mode, and the node group.

### 3. Step 4: the console path, screen by screen

Step 4 of the lesson walks through the AWS Console's **Create cluster** wizard with real screenshots, numbered boxes on
what to click: Custom configuration, switching EKS Auto Mode off, name and cluster IAM role, choosing version 1.37
(the console pre-selected 1.36), cluster access, networking, observability, add-ons, review. Look at every screenshot.
Then notice what the lesson says at the end: the console is good for understanding; a file is better for anything you
want to repeat, review or delete reliably.

### 4. Steps 5–7: create and verify

`eksctl create cluster -f eks/cluster.yaml` took **868.9 seconds (about 14.5 minutes)** in the recorded run. It
ended with:

```text
2026-10-04 15:42:29 [✔]  created 1 managed nodegroup(s) in cluster "k8s-from-zero"
2026-10-04 15:42:29 [ℹ]  creating addon: metrics-server
2026-10-04 15:42:29 [ℹ]  successfully created addon: metrics-server
2026-10-04 15:42:30 [✔]  EKS cluster "k8s-from-zero" in "eu-central-1" region is ready
```

Then the verification checklist from [docs/11](../docs/11-cluster-verification.md), on EKS. What the real run showed,
and what to notice:

```text
NAME                                             STATUS   ROLES    AGE   VERSION               INTERNAL-IP
ip-10-50-110-141.eu-central-1.compute.internal   Ready    <none>   61s   v1.37.0-eks-3b4a6ca   10.50.110.141
ip-10-50-151-189.eu-central-1.compute.internal   Ready    <none>   63s   v1.37.0-eks-3b4a6ca   10.50.151.189
```

Two nodes, both workers. **No control-plane node.**

```text
NAMESPACE     NAME                              READY   STATUS              RESTARTS   AGE
kube-system   aws-node-68mqd                    2/2     Running             0          64s
kube-system   aws-node-tdb5w                    2/2     Running             0          62s
kube-system   coredns-c7b948bf9-5z9n5           1/1     Running             0          4m23s
kube-system   coredns-c7b948bf9-8x7ss           1/1     Running             0          4m23s
kube-system   kube-proxy-cn9pb                  1/1     Running             0          62s
kube-system   kube-proxy-wgxks                  1/1     Running             0          64s
```

No etcd, no API server Pods. `aws-node` is the **Amazon VPC CNI**: Pods get real VPC addresses (`10.50.x.x`), not an
overlay range like Flannel's `10.244.0.0/16`.

```text
NAME   TYPE           CLUSTER-IP       EXTERNAL-IP                                                                  PORT(S)        AGE
web    LoadBalancer   172.20.118.174   a72ba0a318ba641bc93e45e807ae8628-1535282912.eu-central-1.elb.amazonaws.com   80:31399/TCP   3m55s
```

A `LoadBalancer` Service is a NodePort Service (`31399`) with an AWS load balancer in front. The final `curl` through
that DNS name returned `<title>Welcome to nginx!</title>`.

### 5. Step 8: the running cluster in the console

Look at the screenshots of the cluster's tabs. One of them is a lesson in itself: **Compute** and **Resources** show
**Unauthorized**. The screenshots were taken with a separate read-only console identity that had no EKS **access
entry**. AWS permissions are not Kubernetes permissions: to see inside the cluster, an identity needs an access entry
(or, in older clusters, an `aws-auth` mapping).

### 6. Lab 04 · Read a real cluster like an engineer

Do [labs/04](../labs/04-eks-installation.md). It costs nothing: six questions about the recorded outputs, from version
and node count to the traffic path and the hourly cost.

### 7. Cleanup, the same day

Run [eks/cleanup.md](../eks/cleanup.md). **Order matters:** delete the `LoadBalancer` Service first, so Kubernetes
removes the load balancer while the cluster still exists. Otherwise it stays behind, keeps costing money, and blocks
the deletion of the VPC.

In the recorded run, `eksctl delete cluster --wait` took **674.9 seconds (about 11 minutes)**. Then the two checks
that turn "it should be gone" into proof:

```text
Resources of the lab cluster k8s-from-zero in eu-central-1:
  gone  EKS cluster
  gone  CloudFormation stacks
  gone  VPC
  gone  NAT gateways
  gone  Elastic IPs
  gone  EC2 nodes
  gone  EBS volumes
  gone  Load balancers (from Services)
  gone  Security groups
  gone  IAM roles (eksctl-k8s-from-zero-*)

Clean: nothing of k8s-from-zero is left.
```

and the inventory, identical to the one taken before the run.

## Expert commentary

- **Why it matters at work.** On EKS your job is not installing control planes. It is node groups, IAM access, VPC
  design, add-on and cluster upgrades, and **cost**. A forgotten lab cluster costs around $200 a month; a forgotten
  NAT gateway or load balancer keeps billing even after the cluster is gone.
- **Tags and scripts.** Every resource of the lab carries `Project: k8s-from-zero`, and the verify script checks by name,
  by tag and by real state. That is how you clean up in a shared account without touching anyone else's resources.
- **Upgrade policy.** The cluster list showed "Extended support": eksctl kept the AWS default. For a cluster you keep,
  choose Standard, so the cluster is upgraded instead of paying the extended-support fee later.
- **Common mistakes.** Deleting the cluster before the LoadBalancer Services; working in the wrong region; assuming
  `ReadOnlyAccess` lets you see Pods; committing a kubeconfig.
- **What an interviewer asks.** "What does AWS manage in EKS, and what do you?" "How do Pods get IPs on EKS?" "How
  does kubectl authenticate to EKS?" "What would you check before deleting an EKS cluster?"

## Checkpoint

You are done when:

- [ ] you can draw what AWS manages and what lives in your account
- [ ] you can explain every column of the `kubectl get nodes` and `kubectl get service web` outputs above
- [ ] lab 04 is done
- [ ] if you created a cluster: `verify-cleanup.sh` printed `Clean: nothing of k8s-from-zero is left.` and your
      inventory matches the one from before

Next: [09 · Cleanup and comparison](09-cleanup-and-compare.md)
