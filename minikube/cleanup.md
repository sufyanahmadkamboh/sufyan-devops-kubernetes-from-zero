# Minikube · cleanup

> Removes everything the [Minikube lesson](README.md) created.

```text
⚠️ DESTRUCTIVE COMMAND · deletes the "minikube" cluster: the container, its disk and its kubectl context.
```

<!-- test: timeout=300; contains=Removed -->
```bash
minikube delete
```

<!-- test: contains=no Kubernetes containers left -->
```bash
docker ps -a --filter name=minikube --format '{{.Names}}' | grep -q . && echo "still there" || echo "no Kubernetes containers left"
```

`minikube delete --all` removes every profile at once. The downloaded base image stays in Minikube's cache
(`~/.minikube`) so the next start is fast; delete that folder to reclaim the disk space.

## Verification

<!-- test: fail; output -->
```bash
kubectl config get-contexts minikube
```

```text
CURRENT   NAME   CLUSTER   AUTHINFO   NAMESPACE
error: context minikube not found
```

The context is gone, and kubectl no longer knows the cluster.

Back to the [roadmap](../README.md).
