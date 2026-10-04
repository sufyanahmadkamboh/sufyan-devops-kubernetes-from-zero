# 11 · The cluster verification checklist

> Time: 15 minutes · Used at the end of every installation lesson.

"The install finished without errors" is not the same as "the cluster works". Every installation in this course ends
with the **same eight checks**, in the same order, from the bottom (nodes) to the top (an application reachable from
outside). If one fails, the [troubleshooting labs](../troubleshooting/README.md) show how to find out why.

```text
 8  kubectl and cluster versions are compatible              ← your tools
 7  Pods on different nodes can reach each other             ← CNI across nodes
 6  a Service is reachable from outside the cluster          ← kube-proxy / NodePort / load balancer
 5  a test Deployment runs 2 replicas                        ← scheduler, kubelet, runtime, image pulls
 4  cluster DNS resolves Service names                       ← CoreDNS
 3  the API server answers and is healthy                    ← control plane
 2  the system Pods are Running                              ← kube-system
 1  every node is Ready                                      ← kubelet + runtime + CNI on each node
```

## The checks

| # | Check | Pass when |
|---|---|---|
| 1 | `kubectl get nodes -o wide` | every node `Ready`, the expected version, `containerd://…` runtime |
| 2 | `kubectl get pods -A` | all Pods `Running` (or `Completed`), no `CrashLoopBackOff`, `Pending`, `ImagePullBackOff` |
| 3 | `kubectl cluster-info` and `kubectl get --raw='/readyz?verbose'` | the control plane URL is printed; `readyz check passed` |
| 4 | `kubectl run dnstest --image=busybox:1.37 --rm -i --restart=Never --quiet -- nslookup kubernetes.default.svc.cluster.local` | an `Address:` line with the Service IP |
| 5 | `kubectl create deployment web --image=nginx:1.30-alpine --replicas=2` and `kubectl rollout status deployment/web` | `successfully rolled out`, `2/2` ready |
| 6 | expose `web` and `curl` it from outside | `<title>Welcome to nginx!</title>` |
| 7 | `curl` a Pod IP that lives on **another** node | the nginx title again |
| 8 | `kubectl version` | client within one minor version of the server (e.g. 1.36–1.38 for a 1.37 cluster) |

Instead of `kubectl create deployment`, you can also apply the ready-made manifests in
[examples/nginx](../examples/nginx/README.md) (same Deployment, plus health checks and resource requests).

## The same checks on each cluster type

The commands are the ones used in the lessons. `kubectl` is the same everywhere; only how you reach the Service from
outside, and how you open a shell on a node, differ.

| # | kubeadm ([lesson](../kubeadm/README.md)) | Minikube ([lesson](../minikube/README.md)) | MicroK8s ([lesson](../microk8s/README.md)) | EKS ([lesson](../eks/README.md)) |
|---|---|---|---|---|
| 1 | `kubectl get nodes -o wide` (2 nodes) | `kubectl get nodes -o wide` (1 node) | `microk8s kubectl get nodes -o wide` or `kubectl …` after the alias | `kubectl get nodes -o wide` (2 workers, no control-plane nodes) |
| 2 | `kubectl get pods -A`: apiserver, etcd, scheduler, controller-manager, kube-proxy, CoreDNS, Flannel | `kubectl get pods -A`: same control-plane Pods + storage-provisioner | `kubectl get pods -A`: Calico, CoreDNS (control plane is the `kubelite` service, not Pods) | `kubectl get pods -A`: aws-node, kube-proxy, CoreDNS, metrics-server (no control-plane Pods) |
| 3 | `kubectl cluster-info`, `kubectl get --raw='/readyz?verbose'` | `kubectl cluster-info`, `minikube status` | `kubectl cluster-info`, `microk8s status --wait-ready` | `kubectl cluster-info`, `aws eks describe-cluster … --query cluster.status` → `ACTIVE` |
| 4 | `nslookup` from a busybox Pod | same | same | same |
| 5 | `web`, 2 replicas | same | same | same |
| 6 | `--type=NodePort`, `curl http://<worker-ip>:<node-port>` | `--type=NodePort`, `curl "$(minikube service web --url)"` | `--type=NodePort`, `curl http://127.0.0.1:<node-port>` on the VM | `--type=LoadBalancer`, `curl http://<elb-hostname>` (allow 1–3 minutes for DNS) |
| 7 | `curl` a Pod IP from the control plane | needs `--nodes 2` (one node: skip) | one node: skip (multi-node: from another node) | Pods have VPC IPs on both nodes: `kubectl get pods -l app=web -o wide`, then `curl` from a Pod on the other node |
| 8 | `kubectl version` | `kubectl version` | `kubectl version` | `kubectl version` (server shows `v1.37.x-eks-…`) |

## Why this order?

Each check depends on the ones below it. If nodes are `NotReady` (1), Pods will not schedule (5), so there is no point
debugging the Service (6) yet. Always fix the **lowest** failing check first.

| First failing check | Look at |
|---|---|
| 1 | [Troubleshooting 01](../troubleshooting/01-node-not-ready.md), [07](../troubleshooting/07-container-runtime.md) |
| 2 | [Troubleshooting 06](../troubleshooting/06-core-pods-not-running.md) |
| 3 | [Troubleshooting 05](../troubleshooting/05-kubectl-connection.md) |
| 4 | CoreDNS Pods and their logs ([06](../troubleshooting/06-core-pods-not-running.md)) |
| 5 | `kubectl describe pod`: events ([08](../troubleshooting/08-insufficient-resources.md)) |
| 6, 7 | [Troubleshooting 02](../troubleshooting/02-pod-networking.md), firewall/security groups |

## Clean up the test workload

```text
kubectl delete service web
kubectl delete deployment web
```

On EKS, deleting the Service also deletes the AWS load balancer; do it **before** deleting the cluster
([12 · Cleanup](12-cleanup-and-reset.md)).

## Check yourself

<details><summary>Nodes are Ready and all system Pods run, but `curl` to the NodePort times out. Which checks narrow it down?</summary>

Check 5 (are the `web` Pods Running and Ready?), then `kubectl get endpoints web` (does the Service have Pod IPs?), then
check 7 (Pod-to-Pod across nodes). If Pods answer directly but not through the NodePort, look at kube-proxy and firewalls.
</details>

<details><summary>Why is check 7 the one that catches a broken CNI that check 5 may miss?</summary>

Both replicas can be Running and even reachable on their own node while traffic **between** nodes fails (overlay or
routing broken). Only a request to a Pod on another node proves cross-node networking.
</details>

<details><summary>Your kubectl is v1.33 and the cluster v1.37. Is that OK?</summary>

No. kubectl is supported within one minor version of the API server (1.36–1.38 here). Install a matching kubectl.
</details>

<details><summary>On EKS the Service shows `<pending>` under EXTERNAL-IP for a minute. Is the check failed?</summary>

Not yet. AWS creates the load balancer and its DNS name takes a few minutes to resolve. Retry; investigate events
(`kubectl describe service web`) only if it stays pending.
</details>

Next: [12 · Cleanup and reset](12-cleanup-and-reset.md)
