# examples/nginx · the test workload as YAML

> Time: 10 minutes · Works on every cluster from this course.

The lessons create the test workload with two quick commands (`kubectl create deployment` and `kubectl expose`).
In real work you keep it as **YAML files** in Git instead, so the same workload can be applied again, reviewed and
versioned. These files describe the same `web` application, with two additions that real workloads always have:
health checks and resource requests.

| File | What it creates | Use it on |
|---|---|---|
| [deployment.yaml](deployment.yaml) | Deployment `web`: 2 replicas of `nginx:1.30-alpine`, label `app: web`, requests 50m CPU / 32Mi memory, memory limit 64Mi, readiness and liveness probes on `GET /` | every cluster |
| [service-nodeport.yaml](service-nodeport.yaml) | Service `web`, type NodePort, fixed port **30080** on every node | kubeadm, Minikube, MicroK8s |
| [service-loadbalancer.yaml](service-loadbalancer.yaml) | Service `web`, type LoadBalancer: AWS creates a load balancer | Amazon EKS |

## What each part does

```text
 Service "web" ──selects Pods with label app=web──▶ Pod web-…  (Ready? → gets traffic)
   NodePort 30080 / AWS load balancer                Pod web-…  (Ready? → gets traffic)
                                                       ▲
 Deployment "web" ── keeps 2 replicas, replaces failed Pods ┘
```

- **Labels and selector.** The Deployment's `selector` and the Service's `selector` both say `app: web`; that label is
  the only link between them.
- **readinessProbe.** A Pod receives traffic only after `GET /` answers. During a rollout, new Pods join the Service
  only when they are actually ready.
- **livenessProbe.** If `GET /` keeps failing, the kubelet restarts the container.
- **requests** are what the scheduler reserves on a node ([troubleshooting 08](../../troubleshooting/08-insufficient-resources.md));
  the **memory limit** is the hard ceiling (above it the container is OOM-killed).
- **targetPort: http** refers to the container port by **name**, so the port number lives in one place.

## Apply it

On **kubeadm, Minikube or MicroK8s** (from the repository root):

<!-- test: contains=service/web -->
```bash
kubectl apply -f examples/nginx/deployment.yaml -f examples/nginx/service-nodeport.yaml
```

On **Amazon EKS**:

<!-- test: skip -->
```bash
kubectl apply -f examples/nginx/deployment.yaml -f examples/nginx/service-loadbalancer.yaml
```

If the lesson's `web` Deployment and Service already exist, `kubectl apply` updates them in place. On EKS, changing
an existing NodePort Service to LoadBalancer (or the other way round) is allowed; delete the lesson's Service first if
you want a clean start.

## Verify

<!-- test: retry=10; contains=successfully rolled out; contains=30080 -->
```bash
kubectl rollout status deployment/web --timeout=60s
kubectl get pods -l app=web -o wide
kubectl get endpoints web
kubectl get service web
```

`get endpoints` must list two Pod IPs: if it is empty, the selector does not match or the Pods are not Ready.

Then from outside the cluster:

| Cluster | Command |
|---|---|
| kubeadm | `curl -s http://<worker-ip>:30080 \| grep -o '<title>.*</title>'` |
| Minikube | `curl -s "$(minikube service web --url)" \| grep -o '<title>.*</title>'` |
| MicroK8s (on the VM) | `curl -s http://127.0.0.1:30080 \| grep -o '<title>.*</title>'` |
| EKS | `LB=$(kubectl get service web -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')` then `curl -s "http://$LB" \| grep -o '<title>.*</title>'` (DNS takes 1–3 minutes) |

Expected: `<title>Welcome to nginx!</title>`.

<!-- test-run: curl -s "$(minikube service web --url)" | grep -o '<title>.*</title>' | grep -q 'Welcome to nginx' -->

## Clean up

```text
⚠️ DESTRUCTIVE COMMAND · deletes the web Deployment and Service (on EKS also the AWS load balancer).
```

<!-- test: contains=deleted -->
```bash
kubectl delete -f examples/nginx/ --ignore-not-found
```

`kubectl delete -f` on the folder deletes what every file in it describes. On EKS, do this **before** deleting the cluster.

Back to the [verification checklist](../../docs/11-cluster-verification.md)
