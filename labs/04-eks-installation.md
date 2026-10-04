# Lab 04 · EKS: read a real cluster like an engineer

> After the [EKS lesson](../eks/README.md). Time: 30 minutes. **Costs nothing:** you work with the real outputs and
> console screenshots recorded while this repository's EKS cluster was running, so you can do this lab without an AWS
> account. If you have your own cluster from the lesson, run the commands against it as well, then
> [clean up](../eks/cleanup.md) the same day.

## Task

A colleague created an EKS cluster and sends you the outputs below. Without access to their account, answer the
questions a reviewer would ask: what was created, where it runs, who manages what, how traffic reaches the app, and
what it costs per hour.

## Requirements

Answer the six questions, each with the line of output (or the screenshot) that proves your answer:

1. Which Kubernetes version and EKS platform version does the control plane run?
2. How many worker nodes are there, of which instance type, with which operating system and container runtime?
3. Which Pods form the "plumbing" of the cluster, and which component gives Pods their IP addresses?
4. Pods have IP addresses in the same range as the nodes. Why is that different from the kubeadm lab?
5. How does a request from the internet reach an nginx Pod? Name every hop.
6. Which parts are billed per hour while the cluster runs? Estimate the cost per hour.

## Hints

- [docs/10](../docs/10-eks-architecture.md) explains the EKS architecture; [eks/cluster.yaml](../eks/cluster.yaml)
  is what was created.
- The kubeadm lab used the Flannel CNI with its own Pod network `10.244.0.0/16`.
- Look at the `EXTERNAL-IP` of the Service and the `PORT(S)` column.
- Prices: the [Amazon EKS pricing](https://aws.amazon.com/eks/pricing/) and [EC2 On-Demand
  pricing](https://aws.amazon.com/ec2/pricing/on-demand/) pages (Region Europe (Frankfurt)).

## The evidence

From the run recorded in the [EKS lesson](../eks/README.md):

```text
$ aws eks describe-cluster --name k8s-from-zero --query 'cluster.{status:status,version:version,platform:platformVersion}' --output table
|  eks.4   |  ACTIVE  |  1.37     |

$ kubectl get nodes -o wide
NAME                                             STATUS   VERSION               INTERNAL-IP     OS-IMAGE                        CONTAINER-RUNTIME
ip-10-50-110-141.eu-central-1.compute.internal   Ready    v1.37.0-eks-3b4a6ca   10.50.110.141   Amazon Linux 2023.12.20260928   containerd://2.2.7+unknown
ip-10-50-151-189.eu-central-1.compute.internal   Ready    v1.37.0-eks-3b4a6ca   10.50.151.189   Amazon Linux 2023.12.20260928   containerd://2.2.7+unknown

$ kubectl get pods -A
kube-system   aws-node-68mqd                    2/2     Running
kube-system   aws-node-tdb5w                    2/2     Running
kube-system   coredns-c7b948bf9-5z9n5           1/1     Running
kube-system   coredns-c7b948bf9-8x7ss           1/1     Running
kube-system   kube-proxy-cn9pb                  1/1     Running
kube-system   kube-proxy-wgxks                  1/1     Running
kube-system   metrics-server-7584d9c877-dnjfp   0/1     ContainerCreating

$ eksctl get nodegroup --cluster k8s-from-zero
NODEGROUP  STATUS  MIN SIZE  MAX SIZE  DESIRED CAPACITY  INSTANCE TYPE  IMAGE ID                TYPE
workers    ACTIVE  2         2         2                 t3.medium      AL2023_x86_64_STANDARD  managed

$ kubectl get pods -l app=web -o wide
web-6f5d6d9c94-6qgjl   1/1   Running   10.50.159.242   ip-10-50-151-189.eu-central-1.compute.internal
web-6f5d6d9c94-qf8nx   1/1   Running   10.50.101.146   ip-10-50-110-141.eu-central-1.compute.internal

$ kubectl get service web
NAME   TYPE           CLUSTER-IP       EXTERNAL-IP                                     PORT(S)
web    LoadBalancer   172.20.118.174   a72ba0a3...-1535282912.eu-central-1.elb.amazonaws.com   80:31399/TCP
```

(Columns shortened to fit; the full outputs are in the lesson.) The console screenshots of the same cluster are in
[eks/console/](../eks/console/).

## Solution

<details>
<summary>Try it yourself first. Then open the solution.</summary>

1. **Version:** Kubernetes `1.37`, EKS platform version `eks.4` (`describe-cluster`). The kubelets report
   `v1.37.0-eks-…`: Amazon's build of the same release.
2. **Nodes:** 2 × `t3.medium` in the managed node group `workers` (min = max = desired = 2), Amazon Linux 2023,
   containerd 2.2. You never see a control-plane node: it runs in an AWS-owned account.
3. **Plumbing:** `aws-node` (the **Amazon VPC CNI**, one per node: it gives Pods IPs), `kube-proxy` (one per node:
   Service rules), `coredns` (2 replicas: cluster DNS), `metrics-server` (installed as an add-on: `kubectl top`).
   Compare with kubeadm, where you saw `etcd`, `kube-apiserver` etc. as Pods: on EKS they are hidden and managed.
4. **Pod IPs:** the VPC CNI assigns Pods real IP addresses from the VPC subnets (`10.50.x.x`), attached to the node's
   network interfaces. No overlay network as with Flannel (`10.244.0.0/16` + VXLAN): every VPC resource can reach a
   Pod directly, and security groups and VPC flow logs see Pod IPs. The price: Pods consume subnet IPs, and a t3.medium
   can hold only a limited number of Pod IPs (based on its network interfaces).
5. **Traffic path:** internet → the AWS load balancer (DNS name `…elb.amazonaws.com`, created by the cloud controller
   for the `LoadBalancer` Service) → port `31399` (the NodePort) on a worker node → kube-proxy rules → one of the
   `web` Pods on port 80. A `LoadBalancer` Service is a `NodePort` Service plus a cloud load balancer in front.
6. **Hourly cost** (check the current prices on the pages in the hints; Frankfurt, on-demand): the EKS control
   plane (about $0.10/h), 2 × t3.medium EC2 instances, 1 NAT gateway (per hour + per GB), the load balancer (per
   hour + usage), 2 × 20 GB gp3 EBS volumes, plus small amounts of data transfer. Together roughly **$0.25–0.30 per
   hour**: cheap for one afternoon, ~$200 per month if forgotten. That is why the cleanup is part of the lesson.

</details>

## Explanation

Reading outputs precisely is most of the job: version, node count, OS, runtime, CNI and the network path are all in
five commands. On a managed service, part of the architecture is invisible (the control plane), and part is created
for you outside Kubernetes (the load balancer, ENIs, security groups). Those hidden parts are exactly what costs money
and what blocks deletion if forgotten: a `LoadBalancer` Service still present when you delete the cluster leaves an
orphaned load balancer that keeps the VPC from being deleted. See the order in [eks/cleanup.md](../eks/cleanup.md).

Next: [Lab 05 · Which installation for which situation?](05-installation-comparison.md)
