# Amazon EKS · Cleanup

> Run this as soon as you have finished the [EKS lesson](README.md). Every hour the cluster exists costs about
> $0.25-0.30.

```text
⚠️ DESTRUCTIVE COMMAND
This deletes the EKS cluster, the worker nodes, the VPC, the NAT gateway and the IAM roles eksctl created.
Kubernetes objects inside the cluster are lost.
```

**Order matters.** The load balancer was created by Kubernetes, not by eksctl. Delete the Service first, so Kubernetes
removes the load balancer while the cluster still exists; otherwise the load balancer stays behind, keeps costing money,
and blocks the deletion of the VPC.

<!-- test: aws; contains=deleted -->
```bash
kubectl delete service web
kubectl delete deployment web
```

<!-- test: aws; retry=40; timeout=30; contains=gone  Load balancers -->
```bash
eks/scripts/verify-cleanup.sh | grep 'Load balancers'
```

<!-- test: aws; timeout=2700; contains=all cluster resources were deleted; output=tail:6 -->
```bash
eksctl delete cluster -f eks/cluster.yaml --wait
```

```text
...
2026-10-04 16:05:56 [ℹ]  waiting for stack "eksctl-k8s-from-zero-cluster" to get deleted
2026-10-04 16:05:56 [ℹ]  waiting for CloudFormation stack "eksctl-k8s-from-zero-cluster"
2026-10-04 16:06:26 [ℹ]  waiting for CloudFormation stack "eksctl-k8s-from-zero-cluster"
2026-10-04 16:07:23 [ℹ]  waiting for CloudFormation stack "eksctl-k8s-from-zero-cluster"
2026-10-04 16:08:37 [ℹ]  waiting for CloudFormation stack "eksctl-k8s-from-zero-cluster"
2026-10-04 16:08:38 [✔]  all cluster resources were deleted
```

Never trust "it should be gone": check.

<!-- test: aws; contains=Clean: nothing of k8s-from-zero is left.; output -->
```bash
eks/scripts/verify-cleanup.sh
```

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

<!-- test: aws; contains=EKS clusters; output -->
```bash
eks/scripts/inventory.sh
```

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

The inventory matches the one from [Step 2 of the lesson](README.md#step-2--who-am-i-and-where): the account is exactly as we found it.

## What the recorded run cost

From the timestamps in the outputs above and in the lesson (times in UTC; the eksctl log lines show the local time
of the computer that ran it, UTC+2):

| Resource | Existed | |
|---|---|---|
| EKS control plane, VPC, NAT gateway | 13:28 → 14:08 | about 41 minutes |
| 2 × t3.medium worker nodes, 2 × 20 GB gp3 volumes | 13:40 → about 14:00 | about 20 minutes |
| Classic load balancer of the `web` Service | about 13:43 → 13:57 | about 14 minutes |

At on-demand list prices for Europe (Frankfurt) that is roughly **$0.15–0.20** for the whole lesson. The exact
amount shows up in AWS Cost Explorer about a day later. The same cluster forgotten for a month would cost around
**$200**, which is why the cleanup and its verification are part of the lesson, not an afterthought.

Next: [docs/13 · Installation comparison](../docs/13-installation-comparison.md)
