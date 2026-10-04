# Lab 03 · MicroK8s: publish the app through an Ingress

> After the [MicroK8s lesson](../microk8s/README.md), before its cleanup. Time: 20 minutes.

## Task

A NodePort like `31234` is not something you give to users. Publish the `web` application on port **80** under the
host name `web.local`, using the MicroK8s **ingress** add-on.

## Requirements

1. The ingress add-on is enabled and its controller Pod is running.
2. The `web` deployment and Service exist (from the lesson; create them again if you deleted them).
3. An Ingress object sends `http://web.local/` to the `web` Service.
4. `curl` with the host name `web.local` on port 80 returns the nginx welcome page.
5. A request for an unknown host name does **not** reach `web`.

## Hints

- `microk8s enable --help`, `microk8s status`
- The add-on installs the **Traefik** ingress controller (with Helm) in the namespace `ingress`, listening on the
  node's ports 80 and 443. Its IngressClass for MicroK8s is called `public`.
- `kubectl create ingress --help` (look at `--rule` and `--class`).
- Without DNS, send the host name yourself: `curl -H 'Host: web.local' http://127.0.0.1/`.

## Expected result

`curl -H 'Host: web.local' http://127.0.0.1/` shows `Welcome to nginx!`; `curl -H 'Host: other.local' http://127.0.0.1/`
gets a `404` from the ingress controller.

## Solution

<details>
<summary>Try it yourself first. Then open the solution.</summary>

All commands on the MicroK8s machine (🖥️ on k8s-micro):

<!-- test: on=k8s-micro; timeout=600; contains=ingress; output=tail:3 -->
```bash
sudo microk8s enable ingress
```

```text
...
                number: 80

Gateway API is also available. Create HTTPRoute resources for modern routing.
```

<!-- test: on=k8s-micro; retry=90; contains=1/1; output -->
```bash
kubectl get pods -n ingress
```

```text
NAME            READY   STATUS    RESTARTS   AGE
traefik-vc8kp   1/1     Running   0          8s
```

Make sure the application is there (the commands do nothing if it already exists):

<!-- test: on=k8s-micro; retry=60; contains=successfully rolled out -->
```bash
kubectl get deployment web >/dev/null 2>&1 || kubectl create deployment web --image=nginx:1.30-alpine --replicas=2
kubectl get service web >/dev/null 2>&1 || kubectl expose deployment web --port=80 --type=NodePort
kubectl rollout status deployment web --timeout=10s
```

<!-- test: on=k8s-micro; contains=ingress.networking.k8s.io/web created -->
```bash
kubectl create ingress web --class=public --rule="web.local/*=web:80"
```

<!-- test: on=k8s-micro; contains=web.local; output -->
```bash
kubectl get ingress web
```

```text
NAME   CLASS    HOSTS       ADDRESS   PORTS   AGE
web    public   web.local             80      1s
```

<!-- test: on=k8s-micro; retry=60; contains=Welcome to nginx; output -->
```bash
curl -s -H 'Host: web.local' http://127.0.0.1/ | grep -o '<title>.*</title>'
```

```text
<title>Welcome to nginx!</title>
```

<!-- test: on=k8s-micro; contains=404; output -->
```bash
curl -s -o /dev/null -w '%{http_code}\n' -H 'Host: other.local' http://127.0.0.1/
```

```text
404
```

<!-- test: on=k8s-micro; contains=deleted -->
```bash
kubectl delete ingress web
```

</details>

## Explanation

- A **Service** gives Pods one stable address inside the cluster; an **Ingress** is an HTTP routing rule (host name and
  path → Service). The rule does nothing by itself: an **ingress controller** (here Traefik, installed by the add-on)
  reads the rules and does the routing.
- The controller answers every request on port 80; requests matching no rule get its default `404`.
- MicroK8s add-ons are pre-packaged installations: one command instead of finding, configuring and installing the
  controller yourself (the output shows the add-on running Helm for you). In other clusters you would install the same controller with Helm. On EKS the AWS Load
  Balancer Controller turns Ingress objects into Application Load Balancers.
- The successor API, **Gateway API**, does the same with more features; the add-on installed its resource types
  (CRDs) too, as its output shows. The ideas (rule → controller → Service) are the same.

Next: [Lab 04 · EKS](04-eks-installation.md)
