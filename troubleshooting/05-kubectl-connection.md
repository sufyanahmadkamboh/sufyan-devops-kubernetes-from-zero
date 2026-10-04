# 05 · kubectl cannot connect

> Uses the [kubeadm cluster](../kubeadm/README.md). Time: 10 minutes.

## Problem

Two of the most common messages in any Kubernetes job:

- `The connection to the server localhost:8080 was refused`
- `Unable to connect to the server: dial tcp ...: i/o timeout`

Both mean kubectl is talking to the wrong place. To understand why, you need to understand **kubeconfig**.

```text
 kubeconfig file (~/.kube/config, or $KUBECONFIG, or --kubeconfig)
 ├── clusters:  name → API server URL + the cluster's CA certificate
 ├── users:     name → credentials (client certificate, token, or a command such as `aws eks get-token`)
 ├── contexts:  name → (cluster, user, default namespace)
 └── current-context: which context kubectl uses right now
```

## Symptoms

### Case 1: no kubeconfig at all (🖥️ on k8s-cp)

Point kubectl at a file that does not exist, which is what happens on a fresh machine, or for a user who never copied
`admin.conf`:

<!-- test: on=k8s-cp; fail; contains=localhost:8080; output -->
```bash
KUBECONFIG=/tmp/does-not-exist kubectl get nodes
```

```text
E1004 14:51:38.440159    6068 memcache.go:381] "Couldn't get current server API group list" err="Get \"http://localhost:8080/api?timeout=32s\": dial tcp 127.0.0.1:8080: connect: connection refused"
E1004 14:51:38.441127    6068 memcache.go:381] "Couldn't get current server API group list" err="Get \"http://localhost:8080/api?timeout=32s\": dial tcp 127.0.0.1:8080: connect: connection refused"
E1004 14:51:38.442479    6068 memcache.go:381] "Couldn't get current server API group list" err="Get \"http://localhost:8080/api?timeout=32s\": dial tcp 127.0.0.1:8080: connect: connection refused"
E1004 14:51:38.443000    6068 memcache.go:381] "Couldn't get current server API group list" err="Get \"http://localhost:8080/api?timeout=32s\": dial tcp 127.0.0.1:8080: connect: connection refused"
E1004 14:51:38.444571    6068 memcache.go:381] "Couldn't get current server API group list" err="Get \"http://localhost:8080/api?timeout=32s\": dial tcp 127.0.0.1:8080: connect: connection refused"
The connection to the server localhost:8080 was refused - did you specify the right host or port?
```

### Case 2: the wrong API server address

Make a copy of the working kubeconfig whose server address points at a machine that does not exist (as when a cluster
was rebuilt with a new IP, or someone copied a config from another environment):

<!-- test: on=k8s-cp -->
```bash
cp ~/.kube/config /tmp/broken-config
kubectl config set-cluster kubernetes --server=https://10.255.255.1:6443 --kubeconfig /tmp/broken-config
```

<!-- test: on=k8s-cp; fail; timeout=60; contains=10.255.255.1; output -->
```bash
kubectl --kubeconfig /tmp/broken-config get nodes --request-timeout=5s
```

```text
E1004 14:51:44.098819    6089 memcache.go:381] "Couldn't get current server API group list" err="Get \"https://10.255.255.1:6443/api?timeout=5s\": net/http: request canceled while waiting for connection (Client.Timeout exceeded while awaiting headers)"
E1004 14:51:49.099678    6089 memcache.go:381] "Couldn't get current server API group list" err="Get \"https://10.255.255.1:6443/api?timeout=5s\": net/http: request canceled while waiting for connection (Client.Timeout exceeded while awaiting headers)"
E1004 14:51:54.100075    6089 memcache.go:381] "Couldn't get current server API group list" err="Get \"https://10.255.255.1:6443/api?timeout=5s\": net/http: request canceled while waiting for connection (Client.Timeout exceeded while awaiting headers)"
E1004 14:51:59.101008    6089 memcache.go:381] "Couldn't get current server API group list" err="Get \"https://10.255.255.1:6443/api?timeout=5s\": net/http: request canceled while waiting for connection (Client.Timeout exceeded while awaiting headers)"
E1004 14:52:04.102366    6089 memcache.go:381] "Couldn't get current server API group list" err="Get \"https://10.255.255.1:6443/api?timeout=5s\": net/http: request canceled while waiting for connection (Client.Timeout exceeded while awaiting headers)"
Unable to connect to the server: net/http: request canceled while waiting for connection (Client.Timeout exceeded while awaiting headers)
```

## Initial investigation

Before blaming the cluster, ask kubectl what it **thinks** it is talking to.

## Commands

Which kubeconfig file, which context, which server:

<!-- test: on=k8s-cp; contains=kubernetes-admin@kubernetes; output -->
```bash
echo "KUBECONFIG=${KUBECONFIG:-<not set, so ~/.kube/config>}"
kubectl config get-contexts
kubectl config current-context
```

```text
KUBECONFIG=<not set, so ~/.kube/config>
CURRENT   NAME                          CLUSTER      AUTHINFO           NAMESPACE
*         kubernetes-admin@kubernetes   kubernetes   kubernetes-admin   
kubernetes-admin@kubernetes
```

<!-- test: on=k8s-cp; contains=server:; output -->
```bash
kubectl config view --minify --kubeconfig /tmp/broken-config | grep -E 'server:|cluster:|user:|current-context'
kubectl config view --minify | grep -E 'server:'
```

```text
- cluster:
    server: https://10.255.255.1:6443
    cluster: kubernetes
    user: kubernetes-admin
current-context: kubernetes-admin@kubernetes
  user:
    server: https://10.97.7.168:6443
```

## Output interpretation

- **Case 1:** with no kubeconfig, kubectl falls back to its built-in default, `localhost:8080`. Nothing listens there.
  The message mentions `localhost:8080`, so the problem is "no config", not "cluster down".
- **Case 2:** the broken file's `server:` is `https://10.255.255.1:6443`, the good one points at the control plane's
  real address. The `i/o timeout` (no answer at all) confirms nothing is at that address.
- `--minify` shows only the context currently in use: the fastest way to see where kubectl will connect.

## Root cause

kubectl uses the wrong kubeconfig (none at all), or a context whose cluster entry has the wrong server address.

## Fix

Use the right file and the right context. On the control plane, the admin kubeconfig is `/etc/kubernetes/admin.conf`
(copied to `~/.kube/config` in the lesson); for other clusters, the tool that created them writes it (`minikube start`,
`microk8s config`, `eksctl` / `aws eks update-kubeconfig`). With several clusters in one file, switch contexts with
`kubectl config use-context <name>`.

<!-- test: on=k8s-cp -->
```bash
rm -f /tmp/broken-config
unset KUBECONFIG
```

## Verification

<!-- test: on=k8s-cp; contains=k8s-worker; output -->
```bash
kubectl get nodes
```

```text
NAME         STATUS   ROLES           AGE     VERSION
k8s-cp       Ready    control-plane   5m54s   v1.37.1
k8s-worker   Ready    worker          5m18s   v1.37.1
```

## Lesson learned

- `localhost:8080` in an error = kubectl found **no** kubeconfig.
- `i/o timeout` / `no route to host` = the server address is wrong or unreachable. `x509: certificate signed by unknown
  authority` = the CA in the kubeconfig belongs to another cluster. `Unauthorized` / `Forbidden` = the credentials
  are wrong or lack permissions.
- First command when kubectl misbehaves: `kubectl config current-context`, then `kubectl config view --minify`.

Next: [06 · Core Pods not running](06-core-pods-not-running.md)
