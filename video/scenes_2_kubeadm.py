"""Chapters 5-7: the kubeadm cluster, its verification, and troubleshooting it."""

from __future__ import annotations

from components import arrow, box, checklist, label, notes, svg, terminal
from recordings import rec
from scenes_common import KA, LAB, S, TS, scene

# ---------------------------------------------------------------- 5. kubeadm
scene("A full cluster with kubeadm", "docs/05", "What kubeadm init does, phase by phase", checklist([
    (0, "1", "preflight", "checks CPUs, memory, swap, ports, the container runtime; stops before changing anything"),
    (1, "2", "certs + kubeconfig", "a private certificate authority and certificates in /etc/kubernetes/pki; admin.conf"),
    (2, "3", "control-plane + etcd", "writes static Pod manifests to /etc/kubernetes/manifests; the kubelet starts them"),
    (3, "4", "bootstrap-token + addons", "a token for joining workers; installs CoreDNS and kube-proxy"),
]), [
    S("kube admin init builds a control plane in phases. First, preflight: it checks the machine. C P Us, memory, swap, "
      "ports, and whether the container runtime answers. If anything is wrong, it stops before it changes anything."),
    S("Then it creates a private certificate authority and certificates for every component, plus the admin kube config file."),
    S("Then it writes the control plane, A P I server, scheduler, controller manager and etcd, as static Pod manifests. "
      "The kubelet sees those files and starts them."),
    S("Finally it creates a token so workers can join, and installs Core D N S and kube-proxy."),
])

scene(None, "Recorded · kubeadm lesson, step 5", "sudo kubeadm init", terminal(
    rec(KA, "sudo kubeadm init --pod-network-cidr=10.244.0.0/16", tail=12,
        tones={"successfully": "ok", "kubeadm join": "warn", "--discovery-token": "warn"}),
    "k8s-cp (recorded)"), [
    S("Here it is, on the real control plane. One command, with one important option: the Pod network range, ten "
      "two forty four, which our network plugin will use later."),
    S("About a minute later: your Kubernetes control plane has initialized successfully. And at the end, the join "
      "command for workers, with a token and the hash of the cluster's certificate.", zoom=1.2),
])

scene(None, "Recorded · the first surprise", "Ready? Not yet.", terminal(
    rec(KA, "kubectl get nodes", nth=0, tones={"NotReady": "bad"})
    + rec(KA, "kubectl describe node k8s-cp | grep", step=1, wrap=110, tones={"NetworkPluginNotReady": "bad"}),
    "k8s-cp (recorded)"), [
    S("We copy the admin kube config into our home folder, and ask for the nodes. The control plane is there. And it is "
      "Not Ready.", zoom=1.3),
    S("Every beginner thinks something went wrong. Describe the node, and Kubernetes tells you exactly why: network "
      "plugin not ready, C N I plugin not initialized. Nothing is broken. Kubernetes does not ship a Pod network. "
      "You have to choose one and install it.", zoom=1.15),
])

scene(None, "docs/06", "The Pod network: what a CNI plugin does", svg(
    '<rect class="st" data-s="0" x="0" y="20" width="800" height="440" rx="24" fill="#101d31" stroke="#3b82d6" stroke-width="3"/>'
    + label(0, 30, 70, "k8s-cp  192.168.x.10", 26, "sky")
    + box(0, 40, 110, 330, 150, "📦", "Pod 10.244.0.5", ["coredns"], "blue")
    + box(1, 40, 290, 720, 130, "🌉", "cni0 bridge  +  flannel.1 (VXLAN)", ["Pod subnet of this node: 10.244.0.0/24"], "ok", "#0f2a22")
    + '<rect class="st" data-s="0" x="920" y="20" width="800" height="440" rx="24" fill="#101d31" stroke="#3b82d6" stroke-width="3"/>'
    + label(0, 950, 70, "k8s-worker  192.168.x.11", 26, "sky")
    + box(0, 960, 110, 330, 150, "📦", "Pod 10.244.1.7", ["web"], "blue")
    + box(1, 960, 290, 720, 130, "🌉", "cni0 bridge  +  flannel.1 (VXLAN)", ["Pod subnet of this node: 10.244.1.0/24"], "ok", "#0f2a22")
    + arrow(2, 770, 360, 950, 360, "ok", label="Pod packet wrapped in UDP")
    + label(3, 860, 560, "Every Pod gets its own IP. Every Pod can reach every other Pod, on any node, without NAT.", 30, "amber", "middle", 800)
), [
    S("What does a C N I plugin do? Flannel, which we use, gives every node its own slice of the Pod network: ten two "
      "forty four zero on the control plane, ten two forty four one on the worker."),
    S("On each node it creates a bridge for the local Pods, and a tunnel device called flannel one."),
    S("When a Pod talks to a Pod on another node, Flannel wraps the packet in U D P and sends it across, a V X LAN overlay."),
    S("The result is the Kubernetes network model: every Pod has its own I P, and every Pod can reach every other Pod "
      "directly. Remember the node in the middle: it has to forward those packets."),
])

scene(None, "Recorded · kubeadm lesson, step 6", "Install Flannel → Ready", terminal(
    rec(KA, "kube-flannel.yml", tones={"created": "ok"}, width=120)
    + rec(KA, "kubectl wait --for=condition=Ready node/k8s-cp", step=1, tones={"Ready": "ok"})
    + rec(KA, "kubectl get pods -A", step=2, nth=0, width=150, tones={"Running": "ok"}),
    "k8s-cp (recorded)"), [
    S("One kube control apply installs Flannel: a namespace, permissions, its configuration, and a DaemonSet, which "
      "runs one Flannel Pod on every node."),
    S("Seconds later, the control plane is Ready.", zoom=1.3),
    S("And now every system Pod is running: etcd, the A P I server, the controller manager, the scheduler, kube-proxy, "
      "Core D N S, and Flannel. That is the architecture diagram, alive."),
])

scene(None, "Recorded · kubeadm lesson, step 7", "Join the worker", terminal(
    rec(KA, "JOIN=$(multipass exec k8s-cp -- sudo kubeadm token create --print-join-command)", nth=0, tail=5,
        tones={"This node has joined the cluster": "ok"})
    + rec(KA, "kubectl wait --for=condition=Ready node/k8s-worker", step=1, tones={" Ready": "ok"}),
    "bash (recorded)"), [
    S("Now the worker. On the control plane we create a fresh join command, and run it on the worker. Behind the scenes "
      "the worker checks the control plane's certificate against the hash, authenticates with the token, and receives its "
      "own kubelet certificate. This node has joined the cluster.", zoom=1.2),
    S("A few seconds later: two nodes, both Ready. A real Kubernetes cluster, built by hand.", zoom=1.3),
])

# ---------------------------------------------------------------- 6. verify kubeadm
scene("Verify the kubeadm cluster", "docs/11", "The verification checklist (used on every cluster)", checklist([
    (0, "1", "Nodes Ready, system Pods Running", "kubectl get nodes · kubectl get pods -A"),
    (0, "2", "The API is healthy", "kubectl cluster-info · kubectl get --raw='/readyz?verbose'"),
    (1, "3", "A test workload runs", "Deployment web: 2 replicas of nginx:1.30-alpine"),
    (1, "4", "It is reachable from outside", "a Service: NodePort here, LoadBalancer on EKS"),
    (2, "5", "Pods talk across nodes", "curl a Pod IP on another node: the CNI really works"),
]), [
    S("A cluster that says Ready is not yet a cluster you can trust. We use the same verification checklist on every "
      "cluster in this course. First, the nodes and the system Pods, and the health of the A P I server itself."),
    S("Then a real workload: two copies of nginx, and a Service that makes them reachable from outside."),
    S("And the check most people forget: can a Pod on one node reach a Pod on the other node? That is the real test of the network."),
])

scene(None, "Recorded · kubeadm lesson, step 8", "Health, workload, Service", terminal(
    rec(KA, "kubectl get --raw='/readyz?verbose'", tones={"passed": "ok"})
    + rec(KA, "kubectl rollout status deployment/web", step=1, nth=0, width=150, tones={"successfully": "ok"})
    + rec(KA, "NODE_PORT=$(kubectl get service web", step=2, tones={"Welcome to nginx": "ok"}),
    "k8s-cp (recorded)"), [
    S("The A P I server's own health checks: every check passed, ready z check passed.", zoom=1.3),
    S("The web Deployment rolled out, two of two replicas available.", zoom=1.2),
    S("And through the NodePort on the worker's I P: welcome to engine x. The request went into the worker, through "
      "kube-proxy's rules, to a Pod.", zoom=1.3),
])

scene(None, "Recorded · the real network test", "From the control plane to a Pod on the worker", terminal(
    rec(KA, "POD_IP=$(kubectl get pods -l app=web", tones={"Welcome to nginx": "ok"}),
    "k8s-cp (recorded)"), [
    S("Last check. From the control plane, we fetch the page directly from a Pod's I P address. The packet leaves the "
      "control plane through the Flannel tunnel, arrives on the worker and is delivered to the Pod. The answer comes "
      "back. The Pod network works across nodes. The cluster is verified.", zoom=1.3),
])

# ---------------------------------------------------------------- 7. troubleshoot kubeadm
scene("Troubleshoot kubeadm", "Recorded · troubleshooting/01", "A node is NotReady", terminal(
    rec(TS[1], "kubectl get nodes", tones={"NotReady": "bad"})
    + rec(TS[1], "kubectl describe node k8s-worker | sed -n", step=1, grep="Ready|MemoryPressure|stopped", width=150,
          tones={"Unknown": "bad"})
    + rec(TS[1], "systemctl is-active kubelet", step=2, tones={"inactive": "bad"}),
    "bash (recorded)"), [
    S("Now we break it. Troubleshooting lab one: the worker is Not Ready. Someone stopped its kubelet, but we don't "
      "know that yet. All we see is Not Ready.", zoom=1.3),
    S("Describe the node and read the conditions. Every condition says Unknown, and the message: kubelet stopped "
      "posting node status. The control plane has not heard from this node's agent."),
    S("So we look at the agent, on the worker: the kubelet is inactive. Root cause found. Start it, and the node is Ready "
      "within seconds.", zoom=1.3),
])
scene(None, "Recorded · troubleshooting/03", "kubeadm init fails at preflight", terminal(
    rec(TS[3], "sudo kubeadm init --pod-network-cidr=10.244.0.0/16", tail=4, wrap=120, tones={"ERROR": "bad"})
    + rec(TS[3], "systemctl is-active containerd", step=1, tones={"active": "ok"})
    + rec(TS[3], "grep -n 'disabled_plugins'", step=2, tones={"cri": "bad"})
    + rec(TS[3], "containerd.sock version", step=3, nth=1, tones={"RuntimeName": "ok"}),
    "k8s-lab (recorded)"), [
    S("Lab three: a colleague prepared a new machine, and kube admin init fails immediately, in preflight. The error "
      "is about the container runtime."),
    S("Is containerd running? Yes, active. So the process is fine."),
    S("But the configuration file disables a plugin: C R I. The exact interface the kubelet needs. The containerd "
      "package from Docker's repository is configured for Docker, which doesn't need it."),
    S("Write the full default configuration, restart, and crictl gets an answer from the runtime. Preflight passes. "
      "Lesson: running is not the same as working."),
])

scene(None, "Recorded · troubleshooting/04", "A worker cannot join", terminal(
    rec(TS[4], "CP_IP=$(multipass info k8s-cp", nth=0, tones={"succeeded": "ok", "gitVersion": "ok"}, width=150)
    + rec(TS[4], "sudo kubeadm token list", step=1, width=150)
    + rec(TS[4], "CP_IP=$(multipass info k8s-cp", step=2, nth=1, tones={"refused": "bad"}),
    "bash (recorded)"), [
    S("Lab four: a join command from someone's old notes hangs in discovery. Debug it from the bottom up. Can the new "
      "machine reach port six four four three? Succeeded. Does the A P I server answer? Yes, with its version."),
    S("Then the credentials: the token in the old command is not in the cluster's token list. Tokens expire after "
      "twenty-four hours. The fix: always create a fresh join command."),
    S("For comparison, the other classic cause, a firewall. Block port six four four three, and the connection is "
      "refused. Two causes, the same hanging join, and one command, nc, tells them apart in a second."),
])
