# 05 · What kubeadm does, step by step

> Time: 25 minutes · The theory behind Steps 5 and 7 of the [kubeadm lesson](../kubeadm/README.md).

## What kubeadm does, and does not do

| kubeadm **does** | kubeadm does **not** |
|---|---|
| check that the machine is ready (preflight) | create machines or networks |
| create the cluster's certificate authority and every certificate | install or configure the container runtime |
| write the kubeconfig files for admin and components | install the kubelet (it comes from the package) |
| write static Pod manifests for the control plane | install a CNI plugin |
| install CoreDNS and kube-proxy | install add-ons (Ingress, storage, monitoring) |
| create bootstrap tokens and join nodes | make the control plane highly available by itself |
| upgrade a cluster (`kubeadm upgrade`) and renew certificates | back up etcd |

It is a **bootstrapper**: it does the Kubernetes-specific setup correctly, and nothing more. That is why it is also
used inside other tools (kind and Minikube call kubeadm internally).

## The phases of `kubeadm init`

`kubeadm init` is a fixed list of **phases**. You can run any of them alone with `kubeadm init phase <name>`, which
is how troubleshooting [03](../troubleshooting/03-kubeadm-init-failure.md) re-runs only the preflight checks.

| Phase | What happens | What you can see afterwards |
|---|---|---|
| `preflight` | checks CPUs (≥ 2), memory (≥ 1700 MB), swap, free ports, the container runtime through the CRI, required tools; pulls the control-plane images | `[ERROR …]` lines if something is wrong; nothing is changed yet |
| `certs` | creates the cluster CA, the etcd CA, the front-proxy CA and the certificates for API server, kubelet client, etcd peers, service-account signing keys | `/etc/kubernetes/pki/` |
| `kubeconfig` | writes kubeconfig files with client certificates | `/etc/kubernetes/admin.conf`, `super-admin.conf`, `kubelet.conf`, `controller-manager.conf`, `scheduler.conf` |
| `etcd` | writes the static Pod manifest for a local etcd | `/etc/kubernetes/manifests/etcd.yaml` |
| `control-plane` | writes static Pod manifests for the API server, controller manager and scheduler | `/etc/kubernetes/manifests/kube-*.yaml` |
| `kubelet-start` | writes the kubelet's configuration and (re)starts it; the kubelet now starts the static Pods | `/var/lib/kubelet/config.yaml` |
| `wait-control-plane` | waits until the API server answers healthy | the long pause in the output |
| `upload-config` | stores the kubeadm and kubelet configuration in ConfigMaps, for joins and upgrades | `kubectl -n kube-system get cm kubeadm-config` |
| `upload-certs` | (only with `--upload-certs`) shares control-plane certificates encrypted, for HA joins | Secret `kubeadm-certs` |
| `mark-control-plane` | labels and taints the node so normal Pods are not scheduled there | taint `node-role.kubernetes.io/control-plane:NoSchedule` |
| `bootstrap-token` | creates a join token and the RBAC rules that let new nodes use it | `kubeadm token list` |
| `kubelet-finalize` | switches the kubelet to a rotating client certificate | |
| `addon` | installs CoreDNS and kube-proxy | Deployment `coredns`, DaemonSet `kube-proxy` |

### Static Pods

The control plane runs as **static Pods**: the kubelet reads YAML files in `/etc/kubernetes/manifests` and starts
those Pods itself, without the API server. That solves the chicken-and-egg problem (the API server cannot schedule
itself). To change an API server flag, edit its manifest: the kubelet notices and restarts it. The Pods you see in
`kubectl get pods -n kube-system` with the node name as suffix (`kube-apiserver-k8s-cp`) are "mirror" copies.

### Files on a control plane after init

```text
/etc/kubernetes/
├── admin.conf                 cluster-admin kubeconfig (copied to ~/.kube/config in the lesson)
├── super-admin.conf           break-glass kubeconfig (bypasses RBAC); keep it safe
├── kubelet.conf  controller-manager.conf  scheduler.conf
├── manifests/                 etcd.yaml  kube-apiserver.yaml  kube-controller-manager.yaml  kube-scheduler.yaml
└── pki/                       ca.crt ca.key  apiserver.*  apiserver-kubelet-client.*  front-proxy-*  sa.key sa.pub
    └── etcd/                  ca.*  server.*  peer.*  healthcheck-client.*
/var/lib/etcd/                 etcd's data: the whole cluster state
/var/lib/kubelet/              kubelet configuration, Pod volumes
```

The `.key` files are the cluster's crown jewels: anyone with `ca.key` can create an admin certificate.

## How `kubeadm join` works

```text
 worker                                                     control plane
   │ 1. kubeadm join <api>:6443 --token T --discovery-token-ca-cert-hash sha256:H
   │──── fetch cluster-info (public ConfigMap, signed with T) ───►│
   │ 2. check: does the CA in cluster-info hash to H?  ── if not: STOP (protects against a fake control plane)
   │ 3. authenticate with the bootstrap token T ──────────────────►│ token valid? (24 h by default)
   │ 4. TLS bootstrap: kubelet sends a certificate signing request ►│ auto-approved for bootstrap tokens
   │◄─────────────────────────────── signed kubelet client certificate
   │ 5. kubelet starts with its own certificate, registers the Node ► node appears (NotReady until the CNI runs)
```

- The **token** proves the worker is allowed to join. It expires: always create a fresh command with
  `kubeadm token create --print-join-command` ([troubleshooting 04](../troubleshooting/04-worker-join-failure.md)).
- The **CA cert hash** proves to the worker that it is talking to the real control plane.
- After **TLS bootstrapping**, the token is no longer used: the kubelet has its own certificate, which it rotates.

## Production is different

The lesson builds **one** control-plane node. If it fails, the cluster cannot be managed. Production clusters differ:

| Topic | Learning cluster | Production |
|---|---|---|
| Control plane | 1 node | **3** (or 5) control-plane nodes, so etcd keeps a majority when one fails |
| API endpoint | the node's IP | a **load balancer** (or virtual IP) in front of all API servers, set with `kubeadm init --control-plane-endpoint <lb-dns>:6443` from the start (it cannot be added later without pain) |
| Joining control planes | n/a | `kubeadm init --upload-certs`, then `kubeadm join … --control-plane --certificate-key <key>` |
| etcd | stacked (on the control-plane nodes) | stacked, or **external etcd** on dedicated machines for large clusters |
| Certificates | valid 1 year, CA 10 years | monitor with `kubeadm certs check-expiration`; `kubeadm upgrade` renews them; or `kubeadm certs renew all` |
| Upgrades | rebuild | one minor version at a time: `kubeadm upgrade plan`, `kubeadm upgrade apply v1.37.x` on the first control plane, `kubeadm upgrade node` on the others, then drain, upgrade kubelet, uncordon each node |
| Backups | none | scheduled `etcdctl snapshot save`, stored off the cluster, restore tested |
| Machines | prepared by hand or a script | image building (Packer) + configuration management (Ansible) or Cluster API |
| Security | defaults | API server audit logging, encryption of Secrets at rest, Pod Security admission, network policies, restricted SSH |

```text
                 ┌───────────── load balancer :6443 ─────────────┐
                 ▼                       ▼                        ▼
           control-plane-1         control-plane-2         control-plane-3
           apiserver + etcd        apiserver + etcd        apiserver + etcd     ◄── etcd quorum: 2 of 3
                 ▲                       ▲                        ▲
                 └─────────── workers talk only to the load balancer ──────────┘
```

## Check yourself

<details><summary>1. Why does the control plane run as static Pods?</summary>

The kubelet can start static Pods from files without an API server, so the API server itself can run as a Pod. That
solves the bootstrap problem.
</details>

<details><summary>2. kubeadm init failed at preflight. Do you need to reset the machine?</summary>

No. Preflight runs before anything is changed. Fix the cause and run `kubeadm init` again.
</details>

<details><summary>3. What do the token and the CA hash in a join command each protect?</summary>

The token proves to the cluster that the node may join. The CA hash proves to the node that it is talking to the real
control plane.
</details>

<details><summary>4. Why must <code>--control-plane-endpoint</code> be set from the beginning in production?</summary>

It is written into every certificate and kubeconfig. Pointing it at a load balancer from the start lets you add
control-plane nodes later; changing it afterwards means reissuing certificates and configs.
</details>

<details><summary>5. Which file contains everything about your cluster's state, and how do you protect it?</summary>

etcd's data in `/var/lib/etcd`. Protect it with regular `etcdctl snapshot save` backups stored off the cluster, and
practise restoring them.
</details>

Next: [06 · CNI and Pod networking](06-cni-networking.md)
