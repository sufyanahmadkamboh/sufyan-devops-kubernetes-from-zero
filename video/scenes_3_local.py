"""Chapters 8-11: Minikube and MicroK8s, installation and verification."""

from __future__ import annotations

from components import arrow, box, card, grid, label, svg, terminal
from recordings import rec
from scenes_common import EX, LAB, MI, MK, S, TS, scene

# ---------------------------------------------------------------- 8. Minikube installation
scene("Minikube installation", "docs/08", "A whole Kubernetes node in one container", svg(
    '<rect class="st" data-s="0" x="0" y="0" width="1720" height="620" rx="26" fill="#101d31" stroke="#3b82d6" stroke-width="3"/>'
    + label(0, 30, 52, "YOUR COMPUTER  ·  Docker", 26, "sky")
    + '<rect class="st" data-s="1" x="40" y="80" width="1100" height="500" rx="22" fill="#0f2a22" stroke="#4cc286" stroke-width="3"/>'
    + label(1, 70, 130, "container \"minikube\"  (image: kicbase)", 26, "ok")
    + box(1, 70, 160, 500, 170, "🧠", "control plane", ["API server, etcd, scheduler,", "controller manager (static Pods)"], "blue")
    + box(1, 600, 160, 500, 170, "🤖", "kubelet + containerd", ["inside the container", "runs the Pods"], "ok", "#0f2a22")
    + box(2, 70, 370, 1030, 170, "🛠️", "set up with kubeadm, automatically", [
        "the same components you installed by hand, in seconds"], "amber", "#2b2410")
    + box(3, 1190, 80, 500, 230, "⌨️", "kubectl", ["context \"minikube\"", "written to ~/.kube/config"], "violet", "#221a3a")
    + arrow(3, 1190, 200, 1150, 200)
    + box(4, 1190, 350, 500, 230, "🧩", "add-ons and profiles", ["ingress, metrics-server, ...", "several clusters side by side"], "blue")
), [
    S("Minikube takes everything we just built by hand and puts it into a single Docker container on your computer."),
    S("Inside that container is a complete node: the control plane and a kubelet with containerd."),
    S("And here is the fun part: Minikube sets it up with kube admin, automatically. The same tool, the same components, "
      "in seconds instead of an hour."),
    S("It writes a kube control context called minikube, so your normal kube control talks to it."),
    S("On top, add-ons for common extras, and profiles: several independent clusters side by side."),
])

scene(None, "Recorded · Minikube lesson, steps 1–2", "Install and start", terminal(
    rec(MK, "minikube-linux-amd64", tones={"v1.39.0": "ok"})
    + rec(MK, "minikube start --driver=docker", step=1, tail=8, drop=r"kicbase: |\[_", tones={"Done": "ok"}),
    "bash (recorded)"), [
    S("Installation is one binary. Minikube version 1.39.", zoom=1.3),
    S("Then minikube start, with the Docker driver, two C P Us and four gigabytes. It prepares Kubernetes 1.37, "
      "configures the C N I, starts the components, and switches kube control to the new cluster. Done.", zoom=1.15),
])

# ---------------------------------------------------------------- 9. Minikube verification
scene("Minikube verification", "Recorded · the checklist, again", "Status, node, system Pods", terminal(
    rec(MK, "minikube status", tones={"Running": "ok", "Configured": "ok"})
    + rec(MK, "kubectl get nodes -o wide", step=1, width=150, tones={" Ready": "ok"})
    + rec(MK, "docker ps --filter name=minikube", step=2, width=150),
    "bash (recorded)"), [
    S("Same checklist as before. minikube status: host, kubelet and A P I server running, kube config configured."),
    S("One node, Ready, called minikube, running containerd."),
    S("And proof of what we said: the whole node is one Docker container on this machine."),
])

scene(None, "Recorded · Minikube lesson, step 4", "The test workload", terminal(
    rec(MK, "kubectl rollout status deployment/web", width=150, drop="Waiting for", tones={"successfully": "ok"})
    + rec(MK, "URL=$(minikube service web --url)", step=1, tones={"Welcome to nginx": "ok"})
    + rec(MK, "kubectl top nodes", step=2, tones={"minikube": "ok"}),
    "bash (recorded)"), [
    S("The same web Deployment with two replicas, rolled out."),
    S("minikube service web dash dash url gives us an address that reaches the NodePort inside the container. "
      "Welcome to engine x.", zoom=1.3),
    S("And after enabling the metrics server add-on, kube control top shows how much C P U and memory the node uses."),
])

scene(None, "Recorded · profiles and lab 02", "Several clusters, several versions", terminal(
    rec(MK, "kubectl --context multinode get nodes", width=150, grep="NAME|multinode", drop="│", tones={" Ready": "ok"},
        cmd="kubectl --context multinode get nodes")
    + rec(LAB[2], "minikube profile list", step=1, width=150, grep="PROFILE|minikube |prod-like", drop="CURRENT|  prod-like  |  minikube  ",
          cmd="minikube profile list")
    + rec(LAB[2], "kubectl config current-context", step=2, tones={"v1.36": "warn"}),
    "bash (recorded)"), [
    S("Profiles are separate clusters. This one has two nodes: two containers acting as a control plane and a worker."),
    S("In lab two, a third cluster called prod-like runs alongside the main one."),
    S("Because it runs Kubernetes 1.36, the version production still uses. Test against it before you upgrade, then "
      "delete it with one command."),
])

scene(None, "Recorded · troubleshooting/08", "When the laptop is too small, and 300 is not 300m", terminal(
    rec(TS[8], "minikube start -p tiny", tail=4, wrap=118, tones={"memory": "bad"})
    + rec(TS[8], "kubectl get pods -l app=hungry", step=1, tones={"Pending": "bad"})
    + rec(TS[8], "kubectl describe pod -l app=hungry", step=2, grep="FailedScheduling|Insufficient", wrap=118,
          tones={"Insufficient cpu": "bad"})
    + rec(TS[8], "kubectl get deployment hungry -o jsonpath", step=2, tones={"300": "bad"})
    + rec(TS[8], "kubectl rollout status deployment hungry", step=3, width=150, drop="Waiting for", tones={"successfully": "ok"}),
    "bash (recorded)"), [
    S("Troubleshooting lab eight happens here. A cluster with one gigabyte of memory? Minikube refuses before it starts: "
      "Kubernetes alone needs about two."),
    S("Then a small web app that stays Pending. No container, no logs."),
    S("The reason is in the Pod's events, written by the scheduler: no node available, insufficient C P U. And the "
      "Deployment asks for three hundred C P Us. Someone typed three hundred, instead of three hundred M, three "
      "hundred millicores. The scheduler counts requests, not real usage.", zoom=1.15),
    S("Correct the unit, and it rolls out immediately."),
])

# ---------------------------------------------------------------- 10. MicroK8s installation
scene("MicroK8s installation", "docs/09", "All of Kubernetes in one snap package", grid([
    card(0, "📦", "one snap", "sudo snap install microk8s --classic --channel=1.36/stable", "blue"),
    card(1, "⚙️", "kubelite", "API server, scheduler, controller manager, kubelet and proxy in one process", "ok"),
    card(1, "🗄️", "dqlite", "a distributed SQLite instead of etcd; high availability with 3+ nodes", "amber"),
    card(2, "🕸️", "Calico + CoreDNS", "a CNI and DNS, ready after install", "ok"),
    card(2, "🧩", "add-ons", "microk8s enable ingress, metrics-server, hostpath-storage, ...", "violet"),
    card(3, "📌", "channels", "a track per Kubernetes version; snap refreshes within it", "sky"),
], cols=2), [
    S("MicroK8s, from Canonical, takes a different approach. All of Kubernetes is one snap package."),
    S("Inside, the control plane and node components run in one process, kube light, and the cluster state lives in "
      "D Q lite, a distributed version of S Q lite, instead of etcd."),
    S("A C N I, Calico, and Core D N S are ready right after the installation, and add-ons are one command each."),
    S("You choose the Kubernetes version with a channel. We pin 1.36 stable, the newest stable track at the time of "
      "recording, so updates never jump to a new minor version on their own."),
])

scene(None, "Recorded · MicroK8s lesson, steps 2–3", "Install, permissions, ready", terminal(
    rec(MI, "sudo snap install microk8s", tail=1, tones={"installed": "ok"})
    + rec(MI, "groups", step=1, tones={"microk8s": "ok"})
    + rec(MI, "microk8s status --wait-ready", step=2, head=8, tones={"is running": "ok"}),
    "k8s-micro (recorded)"), [
    S("On a fresh Ubuntu machine: one snap install. MicroK8s 1.36 is installed.", zoom=1.3),
    S("We add our user to the microk8s group, so we don't need sudo for every command."),
    S("And microk8s status dash dash wait ready: running. No kube admin init, no C N I to choose. That is the trade: "
      "fewer decisions, less control."),
])

# ---------------------------------------------------------------- 11. MicroK8s verification
scene("MicroK8s verification", "Recorded · the checklist, again", "Node, Pods, and kubelite", terminal(
    rec(MI, "microk8s kubectl get nodes -o wide", width=150, tones={" Ready": "ok"})
    + rec(MI, "microk8s kubectl get pods -A", step=1, width=150, tones={"Running": "ok"})
    + rec(MI, "systemctl list-units 'snap.microk8s.*'", step=2, tones={"kubelite": "ok", "dqlite": "warn"}),
    "k8s-micro (recorded)"), [
    S("The node is Ready, running containerd 2."),
    S("But look at the system Pods: only Calico and Core D N S. Where are the A P I server and etcd?"),
    S("They are not Pods. They are system dee services managed by the snap: kube light, which runs the Kubernetes "
      "components, and k8s D Q lite, the datastore. Same architecture, packaged differently.", zoom=1.2),
])

scene(None, "Recorded · MicroK8s lesson and lab 03", "Workload, NodePort, Ingress", terminal(
    rec(MI, "NODE_PORT=$(kubectl get service web", tones={"Welcome to nginx": "ok"})
    + rec(LAB[3], "kubectl get ingress web", step=1, width=150)
    + rec(LAB[3], "curl -s -H 'Host: web.local'", step=2, tones={"Welcome to nginx": "ok"})
    + rec(LAB[3], "-H 'Host: other.local'", step=3, tones={"404": "bad"}),
    "k8s-micro (recorded)"), [
    S("The web workload answers through its NodePort."),
    S("Lab three goes one step further. The ingress add-on installs the Traefik ingress controller, and an Ingress rule "
      "sends the host name web dot local to the web Service."),
    S("A request for web dot local, on port eighty: welcome to engine x.", zoom=1.3),
    S("Any other host name: four oh four from the controller. One entry point, routing by name. That is what Ingress is for."),
])
