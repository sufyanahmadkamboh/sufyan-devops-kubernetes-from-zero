# Lab 02 · Minikube: test against an older Kubernetes version

> After the [Minikube lesson](../minikube/README.md) and [troubleshooting 08](../troubleshooting/08-insufficient-resources.md).
> Time: 20 minutes.

## Task

Production still runs Kubernetes **1.36**, your laptop cluster runs 1.37. Before a release, you want to check your
manifests against 1.36 too, without touching your main cluster.

## Requirements

1. A second Minikube cluster (profile) called `prod-like`, running Kubernetes **v1.36.0**, with 2 CPUs and 2200 MB.
2. Your main `minikube` cluster keeps running and is not changed.
3. The test deployment from the lesson runs on `prod-like`.
4. You can tell, at any time, which cluster `kubectl` is talking to.
5. `prod-like` is deleted at the end; `minikube` is still there.

## Hints

- `minikube start --help | grep -A2 kubernetes-version`
- `-p` / `--profile` selects the profile for every `minikube` command.
- Minikube names the kubectl context after the profile and switches to it on `start`.
- `kubectl config get-contexts`, `kubectl config use-context`.

## Expected result

`kubectl version` against `prod-like` shows a v1.36 server, `minikube profile list` shows two profiles, and after the
cleanup only `minikube` is left.

## Solution

<details>
<summary>Try it yourself first. Then open the solution.</summary>

<!-- test: timeout=900; contains=Done; output=tail:3 -->
```bash
minikube start -p prod-like --driver=docker --kubernetes-version=v1.36.0 --cpus=2 --memory=2200
```

```text
...
  - Using image gcr.io/k8s-minikube/storage-provisioner:v5
* Enabled addons: default-storageclass, storage-provisioner
* Done! kubectl is now configured to use "prod-like" cluster and "default" namespace by default
```

<!-- test: contains=prod-like; contains=minikube; output -->
```bash
minikube profile list
kubectl config get-contexts
```

```text
┌───────────┬────────┬────────────┬──────────────┬─────────┬────────┬───────┬────────────────┬────────────────────┐
│  PROFILE  │ DRIVER │  RUNTIME   │      IP      │ VERSION │ STATUS │ NODES │ ACTIVE PROFILE │ ACTIVE KUBECONTEXT │
├───────────┼────────┼────────────┼──────────────┼─────────┼────────┼───────┼────────────────┼────────────────────┤
│ minikube  │ docker │ containerd │ 192.168.49.2 │ v1.37.0 │ OK     │ 1     │ *              │                    │
│ prod-like │ docker │ containerd │ 192.168.67.2 │ v1.36.0 │ OK     │ 1     │                │ *                  │
└───────────┴────────┴────────────┴──────────────┴─────────┴────────┴───────┴────────────────┴────────────────────┘
CURRENT   NAME        CLUSTER     AUTHINFO    NAMESPACE
          minikube    minikube    minikube    default
*         prod-like   prod-like   prod-like   default
```

The `*` in `get-contexts` shows `start` switched kubectl to `prod-like`. Check the server version:

<!-- test: contains=v1.36; output -->
```bash
kubectl config current-context
kubectl version | grep Server
```

```text
prod-like
Server Version: v1.36.0
```

<!-- test: contains=deployment.apps/web created -->
```bash
kubectl create deployment web --image=nginx:1.30-alpine --replicas=2
```

<!-- test: retry=60; contains=successfully rolled out; output -->
```bash
kubectl rollout status deployment web --timeout=10s
```

```text
Waiting for deployment "web" rollout to finish: 0 of 2 updated replicas are available...
Waiting for deployment "web" rollout to finish: 1 of 2 updated replicas are available...
deployment "web" successfully rolled out
```

Delete the extra cluster and go back to the main one:

```text
⚠️ DESTRUCTIVE COMMAND · deletes the cluster prod-like.
```

<!-- test: timeout=300; contains=Removed -->
```bash
minikube delete -p prod-like
```

<!-- test: contains=minikube; absent=prod-like; output -->
```bash
kubectl config use-context minikube
minikube profile list
```

```text
Switched to context "minikube".
┌──────────┬────────┬────────────┬──────────────┬─────────┬────────┬───────┬────────────────┬────────────────────┐
│ PROFILE  │ DRIVER │  RUNTIME   │      IP      │ VERSION │ STATUS │ NODES │ ACTIVE PROFILE │ ACTIVE KUBECONTEXT │
├──────────┼────────┼────────────┼──────────────┼─────────┼────────┼───────┼────────────────┼────────────────────┤
│ minikube │ docker │ containerd │ 192.168.49.2 │ v1.37.0 │ OK     │ 1     │ *              │ *                  │
└──────────┴────────┴────────────┴──────────────┴─────────┴────────┴───────┴────────────────┴────────────────────┘
```

</details>

## Explanation

- `--kubernetes-version` picks the version of the control plane and kubelet inside the Minikube node. Your kubectl
  stays at v1.37: Kubernetes supports a client one minor version newer or older than the server.
- Each profile is a separate cluster (its own container, IP and certificates) and a separate kubectl context.
- Testing against the production version before upgrading catches removed APIs early: `kubectl apply` fails
  with `no matches for kind ... in version ...` when a manifest uses an API the server no longer serves.

Next: [Lab 03 · MicroK8s](03-microk8s-installation.md)
