# 06 · Core Kubernetes Pods are not running

> Uses the [kubeadm cluster](../kubeadm/README.md). Time: 15 minutes.

## Problem

Cluster DNS is what lets Pods find Services by name (`web.default.svc.cluster.local`). It is provided by **CoreDNS**,
two Pods in `kube-system`. Someone edited its configuration to "tidy it up". Let's make the same mistake (🖥️ on
k8s-cp). First, a backup, which is exactly what that someone should have made:

<!-- test: on=k8s-cp -->
```bash
kubectl -n kube-system get configmap coredns -o yaml | grep -v '^  resourceVersion:' > coredns-backup.yaml
```

(The backup leaves out `resourceVersion`: that field pins an object to one exact version, and restoring an old
version on top of a newer one would be refused with a `Conflict` error.)

Now the faulty edit: a typo in one directive of the Corefile (`forwardd` instead of `forward`), and a restart of CoreDNS
to pick it up:

<!-- test: on=k8s-cp; contains=restarted -->
```bash
kubectl -n kube-system get configmap coredns -o yaml | sed 's/forward \. /forwardd . /' | kubectl apply -f -
kubectl -n kube-system rollout restart deployment coredns
```

## Symptoms

<!-- test: on=k8s-cp; retry=60; contains=CrashLoopBackOff; output -->
```bash
kubectl get pods -n kube-system -l k8s-app=kube-dns
```

```text
NAME                       READY   STATUS             RESTARTS     AGE
coredns-559f6c778d-gpbqb   1/1     Running            0            5m54s
coredns-6dbd6d75fb-bz9d8   0/1     CrashLoopBackOff   1 (4s ago)   8s
coredns-6dbd6d75fb-qcvfq   0/1     CrashLoopBackOff   1 (3s ago)   8s
```

New CoreDNS Pods crash and restart again and again (`CrashLoopBackOff`). One old Pod still runs: a rolling update keeps
the old version until a new one is healthy. That is the only reason DNS still works at all.

## Initial investigation

For a Pod that is not running: `kubectl get` tells you **that** something is wrong, `kubectl describe` tells you **what
Kubernetes saw**, and `kubectl logs` tells you **what the application said**.

## Commands

<!-- test: on=k8s-cp; contains=Back-off restarting failed container; output -->
```bash
POD=$(kubectl get pods -n kube-system -l k8s-app=kube-dns --field-selector=status.phase!=Succeeded \
  -o jsonpath='{range .items[*]}{.metadata.name} {.status.containerStatuses[0].restartCount}{"\n"}{end}' | sort -k2 -n | tail -1 | cut -d' ' -f1)
echo "Looking at $POD"
kubectl describe pod -n kube-system "$POD" | grep -E 'State:|Reason:|Exit Code:|Restart Count:|Back-off' | head -8
```

```text
Looking at coredns-6dbd6d75fb-qcvfq
    State:          Waiting
      Reason:       CrashLoopBackOff
    Last State:     Terminated
      Reason:       Error
      Exit Code:    1
    Restart Count:  1
  Warning  BackOff    1s (x2 over 2s)  kubelet            spec.containers{coredns}: Back-off restarting failed container coredns in pod coredns-6dbd6d75fb-qcvfq_kube-system(24830367-2fd6-4229-8eac-cbf8e2a151b5)
```

<!-- test: on=k8s-cp; retry=10; contains=forwardd; output -->
```bash
POD=$(kubectl get pods -n kube-system -l k8s-app=kube-dns \
  -o jsonpath='{range .items[*]}{.metadata.name} {.status.containerStatuses[0].restartCount}{"\n"}{end}' | sort -k2 -n | tail -1 | cut -d' ' -f1)
kubectl logs -n kube-system "$POD" --previous --tail=5 || kubectl logs -n kube-system "$POD" --tail=5
```

```text
/etc/coredns/Corefile:13 - Error during parsing: Unknown directive 'forwardd'
maxprocs: Leaving GOMAXPROCS=2: CPU quota undefined
```

## Output interpretation

- `describe`: the container terminated with an error exit code, and Kubernetes keeps restarting it with a growing delay
  (`Back-off restarting failed container`).
- `logs --previous` (the output of the **last crashed** run): CoreDNS refuses to start because of an unknown directive,
  `forwardd`. The application tells you exactly what is wrong; you only have to read it.

## Root cause

An invalid CoreDNS configuration (Corefile) in the ConfigMap `kube-system/coredns`.

## Fix

Restore the backup and restart CoreDNS:

<!-- test: on=k8s-cp; contains=restarted -->
```bash
kubectl apply -f coredns-backup.yaml
kubectl -n kube-system rollout restart deployment coredns
```

## Verification

<!-- test: on=k8s-cp; retry=60; contains=successfully rolled out; output -->
```bash
kubectl -n kube-system rollout status deployment coredns --timeout=10s
kubectl get pods -n kube-system -l k8s-app=kube-dns
```

```text
Waiting for deployment "coredns" rollout to finish: 1 old replicas are pending termination...
Waiting for deployment "coredns" rollout to finish: 1 old replicas are pending termination...
Waiting for deployment "coredns" rollout to finish: 1 old replicas are pending termination...
Waiting for deployment "coredns" rollout to finish: 1 old replicas are pending termination...
Waiting for deployment "coredns" rollout to finish: 1 of 2 updated replicas are available...
deployment "coredns" successfully rolled out
NAME                       READY   STATUS        RESTARTS   AGE
coredns-559f6c778d-gpbqb   1/1     Terminating   0          5m58s
coredns-644c598bdd-cphfn   1/1     Running       0          3s
coredns-644c598bdd-xt86q   1/1     Running       0          3s
```

And DNS really works, from inside a Pod:

<!-- test: on=k8s-cp; retry=10; contains=Address; output=tail:4 -->
```bash
kubectl run dnstest --image=busybox:1.37 --rm -i --restart=Never --quiet -- nslookup web.default.svc.cluster.local
```

```text
...
Address:	10.96.0.10:53

Name:	web.default.svc.cluster.local
Address: 10.108.119.230
```

<!-- test-run on=k8s-cp: rm -f coredns-backup.yaml -->

## Lesson learned

- `get` → `describe` → `logs` (add `--previous` for a container that keeps crashing).
- `CrashLoopBackOff` is not the cause: it is Kubernetes saying "this container keeps exiting". The cause is in the logs.
- Back up a ConfigMap before you edit it, and change system components one small step at a time.
- The same method applies to every system Pod: `kube-proxy`, the CNI Pods, and on kubeadm clusters the static Pods of
  the control plane (for those, also look at `/etc/kubernetes/manifests` and `sudo crictl ps -a` on the node).

Next: [07 · Container runtime problems](07-container-runtime.md)
