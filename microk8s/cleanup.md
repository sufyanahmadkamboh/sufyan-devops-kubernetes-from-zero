# MicroK8s · cleanup

> Removes everything the [MicroK8s lesson](README.md) created.

```text
⚠️ DESTRUCTIVE COMMAND
--purge removes MicroK8s and all its data (every object, every volume) without keeping a snapshot.
```

<!-- test: on=k8s-micro; timeout=600; contains=removed -->
```bash
sudo snap remove microk8s --purge
```

<!-- test: on=k8s-micro; fail -->
```bash
microk8s status
```

On your computer, delete the VM:

```text
⚠️ DESTRUCTIVE COMMAND · deletes the VM k8s-micro.
```

<!-- test: timeout=300 -->
```bash
multipass delete k8s-micro
multipass purge
```

## Verification

<!-- test: absent=k8s-micro; output -->
```bash
multipass list
```

```text
Name          State      IPv4             Image
```

Back to the [roadmap](../README.md).
