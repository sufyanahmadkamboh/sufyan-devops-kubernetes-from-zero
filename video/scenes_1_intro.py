"""Chapters 1-4: introduction, what Kubernetes is, the architecture, the prerequisites."""

from __future__ import annotations

from components import arrow, box, card, checklist, grid, label, notes, svg, terminal, tile
from recordings import rec
from scenes_common import KA, S, scene

# ---------------------------------------------------------------- 1. Introduction
scene("Introduction", "Kubernetes From Zero", "One goal, four ways to get there", svg(
    box(0, 0, 40, 400, 230, "🛠️", "kubeadm", ["a real 2-node cluster", "built by hand on Ubuntu", "every component visible"], "blue")
    + box(1, 440, 40, 400, 230, "💻", "Minikube", ["a whole cluster", "in one container", "on your laptop"], "ok", "#0f2a22")
    + box(2, 880, 40, 400, 230, "📦", "MicroK8s", ["one snap package", "one command", "edge and small servers"], "amber", "#2b2410")
    + box(3, 1320, 40, 400, 230, "☁️", "Amazon EKS", ["a managed cluster", "on AWS", "real cost, real teardown"], "violet", "#221a3a")
    + arrow(4, 860, 300, 860, 400)
    + box(4, 260, 410, 1200, 200, "☸️", "A working Kubernetes cluster you understand", [
        "verified, with a test application, broken on purpose, fixed, and cleaned up",
        "and you know which installation fits which situation"], "blue", "#16306a")
), [
    S("Welcome to Kubernetes From Zero. In this course you will install Kubernetes four different ways. First by hand, "
      "with kube admin, on two Ubuntu machines. That is the one that teaches you how Kubernetes really works."),
    S("Then with Minikube, a complete cluster inside one container on your laptop."),
    S("Then with MicroK8s, a whole Kubernetes in one package with one command."),
    S("And finally on Amazon EKS, where AWS runs the control plane for you, and every hour costs real money."),
    S("Every time, the goal is the same: a cluster you have verified, a test application that answers, a failure you "
      "found and fixed yourself, and a clean machine at the end. By the end you will know which method to choose, and why."),
])

scene(None, "How we work", "Understand → Install → Verify → Break → Troubleshoot → Compare", checklist([
    (0, "1", "Understand", "what each component does, before you install it"),
    (1, "2", "Install and verify", "every step on real machines; the same verification checklist on every cluster"),
    (2, "3", "Break and troubleshoot", "eight realistic failures, investigated the way an engineer does it"),
    (3, "4", "Compare and clean up", "what each method is for; leave nothing behind"),
]), [
    S("This is not a slide show. We will work the way engineers work. First understand what you are about to install."),
    S("Then install it, and verify it, with the same checklist on every cluster."),
    S("Then break it on purpose. Eight troubleshooting labs, each with a real symptom, an investigation and a fix."),
    S("And finally compare the four methods and clean everything up, including the cloud resources."),
])

scene(None, "The repository", "Everything you see is in one free repository", grid([
    card(0, "📚", "docs/", "13 concept lessons, from \"what is Kubernetes\" to choosing an installation", "blue"),
    card(0, "🛠️", "kubeadm/ minikube/ microk8s/ eks/", "the four installation lessons, each with its cleanup", "ok"),
    card(1, "🔧", "troubleshooting/", "8 labs: break it, investigate, fix, verify", "bad"),
    card(1, "🎯", "labs/ capstone/", "5 challenges and the final scenario, solutions hidden", "amber"),
    card(2, "✅", "Tested", "every command runs on fresh virtual machines in CI; the outputs you see are real", "ok"),
    card(2, "🧭", "tutorial/", "the guided path through the repository, chapter by chapter", "violet"),
], cols=2), [
    S("Everything in this video comes from one free repository on GitHub. The docs explain the concepts, and each "
      "installation method has its own lesson with a cleanup page."),
    S("The troubleshooting folder has the eight failure labs, and labs and capstone have challenges with hidden solutions."),
    S("And this is important: every command in the lessons is executed automatically on fresh virtual machines. "
      "Every terminal in this video shows real output from those runs. Nothing is typed by hand for the camera."),
])

# ---------------------------------------------------------------- 2. What Kubernetes is
scene("What Kubernetes is", "The problem", "Containers are easy. Many containers on many machines are not.", svg(
    box(0, 0, 30, 520, 300, "🖥️", "server-1", ["web ×2, api ×1", "", "at 3 a.m. the disk fails"], "bad", "#2a1520")
    + box(0, 600, 30, 520, 300, "🖥️", "server-2", ["api ×2, db ×1", "", "full: no room for more"], "amber", "#2b2410")
    + box(0, 1200, 30, 520, 300, "🖥️", "server-3", ["web ×1", "", "almost empty"], "ok", "#0f2a22")
    + label(1, 860, 420, "Who restarts the web containers somewhere else? Who decides where the new api goes?", 30, "amber", "middle", 800)
    + label(2, 860, 490, "Who updates 40 containers without downtime? Who tells web where api is now?", 30, "amber", "middle", 800)
    + label(3, 860, 600, "Without an orchestrator: you, by hand, every time.", 36, "bad", "middle", 900)
), [
    S("Running one container is easy. But a real company runs hundreds of containers on many machines."),
    S("When a server dies at three in the morning, who restarts its containers somewhere else? When a new copy is "
      "needed, which machine has room?"),
    S("Who updates forty containers to a new version without downtime? And how do the containers find each other when "
      "they keep moving?"),
    S("Without an orchestrator, the answer is: you, by hand, every time. Kubernetes is the orchestrator that does it for you."),
])

scene(None, "The core idea", "You describe the desired state. Kubernetes makes it true, forever.", svg(
    box(0, 0, 60, 480, 210, "📝", "You declare", ["\"web: 2 replicas of nginx:1.30\"", "kubectl apply -f web.yaml"], "blue")
    + arrow(0, 490, 165, 600, 165)
    + box(1, 610, 60, 480, 210, "👀", "Kubernetes observes", ["what is actually running?", "1 replica (one node died)"], "amber", "#2b2410")
    + arrow(1, 1100, 165, 1210, 165)
    + box(2, 1220, 60, 500, 210, "⚙️", "and acts", ["desired 2, actual 1", "→ start one more on a healthy node"], "ok", "#0f2a22")
    + arrow(3, 1470, 280, 1470, 380)
    + arrow(3, 1460, 470, 260, 470)
    + arrow(3, 240, 460, 240, 280)
    + label(3, 860, 450, "the reconciliation loop: observe → compare → act, every few seconds", 28, "sky", "middle")
    + label(4, 860, 600, "Self-healing · scheduling · service discovery · rolling updates · scaling", 32, "ok", "middle", 800)
), [
    S("The core idea is simple. You do not give Kubernetes commands like start this container on that server. You "
      "describe the result you want: the web application, two copies, this image."),
    S("Kubernetes constantly observes what is really running. Say a node died, and only one copy is left."),
    S("It compares: desired two, actual one. And it acts: it starts another copy on a healthy machine."),
    S("This loop, observe, compare, act, runs all the time, for every object in the cluster. It is called reconciliation."),
    S("Self-healing, scheduling, service discovery, rolling updates and scaling all come from this one idea."),
])

# ---------------------------------------------------------------- 3. Architecture
scene("Kubernetes architecture", "docs/02", "The control plane and the nodes", svg(
    '<rect class="st" data-s="0" x="0" y="0" width="820" height="700" rx="26" fill="#101d31" stroke="#3b82d6" stroke-width="3"/>'
    + label(0, 30, 50, "CONTROL PLANE (the brain)", 26, "sky")
    + box(0, 30, 80, 370, 150, "🚪", "kube-apiserver", ["the only front door", "everything talks to it"], "blue")
    + box(0, 420, 80, 370, 150, "🗄️", "etcd", ["the cluster's database", "all desired state"], "amber", "#2b2410")
    + box(1, 30, 260, 370, 150, "📍", "kube-scheduler", ["picks a node", "for each new Pod"], "blue")
    + box(1, 420, 260, 370, 150, "🔁", "controller-manager", ["the reconciliation loops", "Deployments, nodes, ..."], "blue")
    + box(2, 30, 450, 760, 200, "☁️", "cloud-controller-manager (in the cloud only)", [
        "creates load balancers, routes, volumes in AWS / Azure / GCP"], "violet", "#221a3a")
    + '<rect class="st" data-s="3" x="900" y="0" width="820" height="700" rx="26" fill="#0f2a22" stroke="#4cc286" stroke-width="3"/>'
    + label(3, 930, 50, "EVERY NODE (the muscle)", 26, "ok")
    + box(3, 930, 80, 760, 150, "🤖", "kubelet", ["the node agent: starts and watches the Pods assigned to this node"], "ok", "#0f2a22")
    + box(4, 930, 260, 760, 150, "📦", "container runtime (containerd, via CRI)", ["pulls images, runs the containers (runc)"], "ok", "#0f2a22")
    + box(5, 930, 450, 370, 200, "🔀", "kube-proxy", ["Service rules", "(iptables)"], "ok", "#0f2a22")
    + box(5, 1320, 450, 370, 200, "🕸️", "CNI plugin", ["Pod network,", "Pod IP addresses"], "ok", "#0f2a22")
), [
    S("Here is what you are about to install. On the left, the control plane: the brain of the cluster. The A P I "
      "server is the only front door. You, the nodes and every component talk only to it. Behind it, etcd stores the "
      "complete state of the cluster: everything you ever declared."),
    S("The scheduler decides on which node each new Pod runs. The controller manager runs the reconciliation loops we "
      "just saw."),
    S("In a cloud there is one more: the cloud controller manager, which creates load balancers and volumes."),
    S("On the right, every node. The kubelet is the node's agent: it watches the A P I server for Pods assigned to its "
      "node, and makes them run."),
    S("It does not run containers itself. It asks the container runtime, containerd, through an interface called C R I."),
    S("kube-proxy turns Services into network rules, and the C N I plugin gives every Pod its own I P address and "
      "connects Pods across nodes. Keep this picture in mind. We will install every one of these pieces by hand."),
])

scene(None, "docs/02", "What happens when you run kubectl apply", checklist([
    (0, "1", "kubectl → API server", "the Deployment is validated and stored in etcd"),
    (1, "2", "controller-manager", "sees a Deployment without Pods: creates a ReplicaSet, which creates 2 Pod objects"),
    (2, "3", "scheduler", "sees 2 Pods without a node: picks a node for each (free CPU, memory, rules)"),
    (3, "4", "kubelet on that node", "sees a Pod assigned to it: asks containerd to pull the image and start the container"),
    (4, "5", "CNI + kube-proxy", "the Pod gets an IP; Services route traffic to it"),
]), [
    S("Let's follow one command through the cluster. kube control apply sends your Deployment to the A P I server, "
      "which validates it and stores it in etcd. Nothing runs yet."),
    S("The controller manager notices a Deployment without Pods, and creates the Pod objects."),
    S("The scheduler notices Pods without a node, and assigns each one to a node with enough free resources."),
    S("The kubelet on that node notices a Pod assigned to it, and asks containerd to pull the image and start the container."),
    S("Finally the C N I gives the Pod an I P address, and kube-proxy makes the Service send traffic to it. "
      "Five components, each doing one job, all through the A P I server."),
])

scene(None, "docs/07", "Same components, different places", grid([
    card(0, "🛠️", "kubeadm", "control plane = static Pods on your control-plane machine; you run everything", "blue"),
    card(1, "💻", "Minikube", "a whole node (with kubeadm inside) running as one Docker container", "ok"),
    card(2, "📦", "MicroK8s", "all components in one process (kubelite), dqlite instead of etcd, installed by snap", "amber"),
    card(3, "☁️", "Amazon EKS", "control plane in an AWS-owned account, invisible to you; you run the nodes", "violet"),
], cols=2), [
    S("Every installation method runs these same components. What changes is where they live. With kube admin, the "
      "control plane runs as Pods on your control-plane machine, and you are responsible for all of it."),
    S("Minikube packs an entire node into one Docker container on your laptop."),
    S("MicroK8s runs all the components in a single process called kube light, and replaces etcd with a lighter database."),
    S("And on EKS, AWS runs the control plane in its own account. You never even see it. You only run the worker nodes."),
])

# ---------------------------------------------------------------- 4. Prerequisites
scene("Prerequisites", "Recorded · kubeadm lesson, step 1", "Two Ubuntu 24.04 machines", terminal(
    rec(KA, "multipass launch 24.04 --name k8s-cp", tail=2, tones={"Launched": "ok"})
    + rec(KA, "multipass list", step=1, tones={"Running": "ok"}),
    "bash (recorded)"), [
    S("Time to build. For kube admin we need two machines: a control plane with two C P Us and four gigabytes of memory, "
      "and a worker. Multipass creates Ubuntu virtual machines with one command, on Windows, mac O S and Linux."),
    S("Two machines, both running, each with its own I P address. Everything from here on happens inside them.", zoom=1.25),
])

scene(None, "docs/03 · why each prerequisite exists", "Prepare Linux for Kubernetes", notes([
    (0, "Swap off", "the kubelet's memory accounting assumes memory limits are real; by default it refuses to start with swap"),
    (1, "Kernel modules overlay + br_netfilter", "overlay for container filesystems; br_netfilter so bridged Pod traffic passes iptables"),
    (2, "sysctls: ip_forward, bridge-nf-call-iptables", "the node must route packets between Pods, nodes and the outside"),
    (3, "Time sync, unique hostname, open ports", "certificates need correct clocks; 6443 API, 10250 kubelet, 2379-2380 etcd, 30000-32767 NodePorts"),
]), [
    S("Before Kubernetes, Linux needs four kinds of preparation, and each one has a reason. Swap goes off, because the "
      "kubelet's memory management assumes that memory limits are real."),
    S("Two kernel modules: overlay for container file systems, and B R net filter, so that traffic between Pods on a "
      "Linux bridge goes through I P tables, where Kubernetes Services live."),
    S("Two kernel settings: I P forwarding, so the node can route Pod traffic, and the bridge setting that makes "
      "bridged traffic visible to I P tables. Remember I P forward. We will break it later."),
    S("And the basics: synchronised clocks for the certificates, unique host names, and the ports the components use, "
      "like six four four three for the A P I server and ten two fifty for the kubelet."),
])

scene(None, "Recorded · on both machines", "Swap, modules, sysctls", terminal(
    rec(KA, "sudo swapoff -a", cmd="sudo swapoff -a\nsudo sed -i '/ swap / s/^/#/' /etc/fstab")
    + rec(KA, "lsmod | grep -E '^(overlay|br_netfilter)'", step=1, tones={"= 1": "ok"}),
    "k8s-cp (recorded)"), [
    S("On both machines: swap off, now and after every reboot."),
    S("Then the modules and the kernel settings, written to files so they survive a reboot. The check shows both "
      "modules loaded, and forwarding and bridge filtering set to one.", zoom=1.3),
])

scene(None, "Recorded · kubeadm lesson, step 3", "The container runtime: containerd 2", terminal(
    rec(KA, "containerd config default | sudo tee /etc/containerd/config.toml", cmd=(
        "containerd config default | sudo tee /etc/containerd/config.toml > /dev/null\n"
        "sudo sed -i 's/SystemdCgroup = false/SystemdCgroup = true/' /etc/containerd/config.toml\n"
        "sudo systemctl restart containerd"), tones={"SystemdCgroup = true": "ok"})
    + rec(KA, "containerd --version", step=1, tones={"active": "ok"})
    + rec(KA, "kubeadm version -o short", step=2, tones={"v1.37": "ok"}),
    "k8s-cp (recorded)"), [
    S("Now the container runtime. We install containerd 2 from Docker's package repository. Then one detail that breaks "
      "many first installations: we write containerd's full default configuration and switch on the systemd C group "
      "driver, so containerd and the kubelet manage resources the same way."),
    S("containerd is active. The kubelet will talk to it through the C R I socket.", zoom=1.3),
    S("Finally kube admin, kubelet and kube control, version 1.37, from the official Kubernetes package repository, "
      "and held, so a routine system update can never upgrade the cluster by accident.", zoom=1.3),
])
