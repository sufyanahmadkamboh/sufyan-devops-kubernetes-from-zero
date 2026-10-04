# 09 · How MicroK8s works inside

> Time: 15 minutes · Read it before or after the [MicroK8s lesson](../microk8s/README.md).

MicroK8s is Canonical's Kubernetes distribution packed as a single **snap** package. One `snap install` gives you a
complete, conformant cluster on one Linux machine, and a few more commands turn several machines into a
highly-available cluster. This chapter explains what is in that package and why it behaves the way it does.

## Snap packaging

A snap is a self-contained package: the application and everything it needs (here: Kubernetes, containerd, the CNI,
the datastore) in one compressed, read-only image, mounted at `/snap/microk8s/<revision>`.

| Snap idea | What it means for MicroK8s |
|---|---|
| **Track** | the Kubernetes minor version, e.g. `1.36` |
| **Risk level** | `stable`, `candidate`, `beta`, `edge`; the lesson uses `--channel=1.36/stable` |
| **Revision** | every update is a new revision; the previous one is kept, so `snap revert microk8s` rolls back |
| **Confinement** | MicroK8s is installed with `--classic`: it needs broad access to the host (networking, cgroups, mounts) like any Kubernetes node |
| **Writable data** | configuration and state live in `/var/snap/microk8s/current/` (e.g. the component arguments in `args/`) |

### Updates happen on their own

snapd refreshes installed snaps automatically (by default several times a day it checks for new revisions). Within a
track, MicroK8s only receives **patch** releases (1.36.x → 1.36.y); it never jumps to a new minor version unless you
change the track (`sudo snap refresh microk8s --channel=1.37/stable`). On a production machine, control when refreshes
happen with `sudo snap refresh --hold=… microk8s` or a refresh timer (`snap set system refresh.timer=…`), so a node
does not restart its Kubernetes services in the middle of the day.

## Kubelite: the control plane in one process

On a kubeadm cluster the API server, scheduler and controller manager run as separate static Pods, and kube-proxy as
a DaemonSet. MicroK8s runs them **together in one process, `kubelite`**, as a systemd service:

```text
 Ubuntu machine (k8s-micro)
 ├── snap.microk8s.daemon-kubelite      kube-apiserver + kube-scheduler + kube-controller-manager
 │                                      + kubelet + kube-proxy, all in ONE process
 ├── snap.microk8s.daemon-containerd    the container runtime (its own containerd, separate from any Docker)
 ├── snap.microk8s.daemon-k8s-dqlite    the datastore (instead of etcd)
 ├── snap.microk8s.daemon-cluster-agent joins and manages other nodes (microk8s add-node / join)
 └── Pods
     ├── calico-node, calico-kube-controllers   the CNI
     ├── coredns
     └── your Pods (web, ...)
```

That is why the lesson's `systemctl list-units 'snap.microk8s.*'` lists services, and why
`kubectl get pods -n kube-system` shows **no** `kube-apiserver` or `etcd` Pods on MicroK8s: they are not Pods here.

## dqlite instead of etcd

The cluster state (every object you create) is stored in **dqlite**: a distributed SQLite with Raft replication, made
by Canonical. It plays exactly the role etcd plays in the [architecture](02-kubernetes-architecture.md). With one node
it is a local database; with three or more nodes it is replicated automatically.

## Networking: Calico by default

MicroK8s enables **Calico** as its CNI out of the box, so a fresh one-node cluster is `Ready` without you applying a
network plugin (compare the kubeadm lesson, where the node stays `NotReady` until you install Flannel, see
[06 · CNI](06-cni-networking.md)).

## Add-ons

Most extras are one command away: `microk8s enable hostpath-storage`, `metrics-server`, `dns` (CoreDNS, enabled by
default in current releases), `ingress`, `dashboard`, `registry`, `metallb`, `rbac`, ... `microk8s status` lists them
as enabled or disabled. Under the hood an add-on is a script that applies Kubernetes manifests or Helm charts.

## `microk8s kubectl` and the alias

MicroK8s ships its own kubectl, matching the cluster version, as `microk8s kubectl`. You can:

| Option | Command | Note |
|---|---|---|
| use it directly | `microk8s kubectl get nodes` | always matches the cluster |
| alias it | `sudo snap alias microk8s.kubectl kubectl` | done in the lesson; then plain `kubectl` works |
| use your own kubectl | `microk8s config > ~/.kube/config` | exports the admin kubeconfig, e.g. for a laptop |

## Groups and permissions

MicroK8s commands need access to files that belong to root. Instead of typing `sudo` every time, add your user to the
`microk8s` group (`sudo usermod -a -G microk8s "$USER"`). Group changes apply to **new** logins only, which is why the
lesson uses `newgrp microk8s` (or log out and in again). Membership in this group is effectively cluster-admin: grant
it only to people who should administer the cluster.

## High availability with three or more nodes

```text
 on the first node:   microk8s add-node          → prints a "microk8s join <ip>:25000/<token>" command
 on each new node:    microk8s join <ip>:25000/<token>
```

From three control-plane nodes on, MicroK8s turns on HA automatically: dqlite replicates to the voters and the
API server runs on every node. `microk8s status` then shows `high-availability: yes`. Nodes joined with `--worker` run
workloads only.

## Check yourself

<details><summary>Why are there no kube-apiserver or etcd Pods on a MicroK8s cluster?</summary>

The control plane runs inside the single `kubelite` process (a systemd service), and the datastore is dqlite, run by its
own `k8s-dqlite` service. Neither is a Pod.
</details>

<details><summary>You installed with `--channel=1.36/stable`. Will snapd upgrade you to Kubernetes 1.37 overnight?</summary>

No. Automatic refreshes stay inside the track (1.36.x patch releases). Moving to 1.37 needs
`snap refresh microk8s --channel=1.37/stable`. Patch refreshes do restart the services, so control their timing in production.
</details>

<details><summary>Why is a fresh MicroK8s node Ready immediately, when a fresh kubeadm node is NotReady?</summary>

MicroK8s installs Calico as its CNI automatically. kubeadm installs no network plugin; you apply one yourself.
</details>

<details><summary>After `usermod -a -G microk8s`, `microk8s status` still says permission denied. Why?</summary>

Group membership is read at login. Start a new login shell (`newgrp microk8s`, or log out and in).
</details>

<details><summary>How many nodes do you need for MicroK8s high availability?</summary>

Three or more control-plane nodes; HA switches on automatically when the third joins.
</details>

Next: [10 · Amazon EKS architecture](10-eks-architecture.md)
