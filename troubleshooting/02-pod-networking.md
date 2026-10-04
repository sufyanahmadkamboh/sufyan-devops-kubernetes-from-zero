# 02 · Pod networking does not work (but everything looks green)

> Uses the [kubeadm cluster](../kubeadm/README.md). Time: 15 minutes.

## Problem

The nastiest networking problems are the ones where every status is green. First, prove that cross-node Pod traffic
works right now (🖥️ on k8s-cp). The `web` Pods run on the worker; we call one of them from the control plane:

<!-- test: on=k8s-cp; retry=20; contains=Welcome to nginx; output -->
```bash
POD_IP=$(kubectl get pods -l app=web -o jsonpath='{.items[0].status.podIP}')
curl -s --max-time 5 "http://$POD_IP" | grep -o '<title>.*</title>'
```

```text
<title>Welcome to nginx!</title>
```

Now we break it on purpose, the way a hardening script, or a reboot of a machine whose setting was never made
permanent, would do it (🖥️ on k8s-worker):

<!-- test: on=k8s-worker -->
```bash
sudo sysctl -w net.ipv4.ip_forward=0
```

## Symptoms

The same request now hangs and times out:

<!-- test: on=k8s-cp; fail; contains=timed out; output -->
```bash
POD_IP=$(kubectl get pods -l app=web -o jsonpath='{.items[0].status.podIP}')
curl -sS --max-time 5 "http://$POD_IP"
```

```text
curl: (28) Connection timed out after 5002 milliseconds
```

And yet the cluster looks perfectly healthy:

<!-- test: on=k8s-cp; contains=Running; absent=NotReady; output -->
```bash
kubectl get nodes
kubectl get pods -l app=web -o wide
kubectl get pods -n kube-flannel -o wide
```

```text
NAME         STATUS   ROLES           AGE    VERSION
k8s-cp       Ready    control-plane   109s   v1.37.1
k8s-worker   Ready    worker          73s    v1.37.1
NAME                   READY   STATUS    RESTARTS   AGE   IP           NODE         NOMINATED NODE   READINESS GATES
web-6f5d6d9c94-2zks8   1/1     Running   0          62s   10.244.1.3   k8s-worker   <none>           <none>
web-6f5d6d9c94-fl5c7   1/1     Running   0          62s   10.244.1.2   k8s-worker   <none>           <none>
NAME                    READY   STATUS    RESTARTS   AGE   IP            NODE         NOMINATED NODE   READINESS GATES
kube-flannel-ds-42g26   1/1     Running   0          98s   10.97.7.168   k8s-cp       <none>           <none>
kube-flannel-ds-5mxcw   1/1     Running   0          73s   10.97.7.171   k8s-worker   <none>           <none>
```

## Initial investigation

Work from the outside in, one layer at a time:

1. Is the Pod running and listening? (inside the Pod)
2. Is the pod network (Flannel) running on both nodes?
3. Does the worker know how to deliver traffic to the Pod?
4. Does the worker's kernel actually **forward** traffic between interfaces?

## Commands

1. The Pod answers locally, so the application is fine:

<!-- test: on=k8s-cp; contains=Welcome to nginx -->
```bash
kubectl exec deploy/web -- wget -qO- http://127.0.0.1 | grep -o '<title>.*</title>'
```

2. Flannel runs on both nodes (output above: one `kube-flannel-ds` Pod per node, `Running`).

3. On the worker (🖥️ on k8s-worker), the VXLAN interface and the routes for the pod network exist:

<!-- test: on=k8s-worker; contains=flannel.1; contains=cni0; output -->
```bash
ip -brief link show | grep -E 'flannel|cni0'
ip route | grep 10.244
```

```text
flannel.1        UNKNOWN        8e:7b:f1:45:ba:6a <BROADCAST,MULTICAST,UP,LOWER_UP> 
cni0             UP             76:b2:64:36:af:cc <BROADCAST,MULTICAST,UP,LOWER_UP> 
10.244.0.0/24 via 10.244.0.0 dev flannel.1 onlink 
10.244.1.0/24 dev cni0 proto kernel scope link src 10.244.1.1 
```

4. And the kernel setting that lets traffic pass from `flannel.1` to `cni0`:

<!-- test: on=k8s-worker; contains=net.ipv4.ip_forward = 0; output -->
```bash
sysctl net.ipv4.ip_forward
```

```text
net.ipv4.ip_forward = 0
```

## Output interpretation

Packets for the Pod arrive at the worker through the VXLAN tunnel on `flannel.1`, and must be **forwarded** to the
Pod's bridge `cni0`. With `net.ipv4.ip_forward = 0` the kernel drops them. Nothing in Kubernetes is "down", so every
status stays green: the traffic simply disappears.

## Root cause

IP forwarding is off on the worker. Kubernetes networking needs it on every node (that is why the [kubeadm
prerequisites](../kubeadm/README.md) set it in `/etc/sysctl.d/k8s.conf`).

## Fix

Turn it on again, and reload all sysctl files so the permanent setting is the one in effect:

<!-- test: on=k8s-worker; contains=net.ipv4.ip_forward = 1 -->
```bash
sudo sysctl --system > /dev/null
sysctl net.ipv4.ip_forward
```

## Verification

<!-- test: on=k8s-cp; retry=20; contains=Welcome to nginx; output -->
```bash
POD_IP=$(kubectl get pods -l app=web -o jsonpath='{.items[0].status.podIP}')
curl -s --max-time 5 "http://$POD_IP" | grep -o '<title>.*</title>'
```

```text
<title>Welcome to nginx!</title>
```

## Lesson learned

- Green statuses do not prove that traffic flows. Test it: **from one node to a Pod on another node**.
- Debug networking in layers: the app inside the Pod → the CNI Pods → interfaces and routes on the node → kernel
  settings (`ip_forward`, `br_netfilter`) → firewalls between nodes (Flannel needs UDP 8472).
- Kernel settings must be persistent (`/etc/sysctl.d/`), or they silently disappear after the next reboot.

Next: [03 · kubeadm init fails](03-kubeadm-init-failure.md)
