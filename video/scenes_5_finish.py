"""Chapters 14-18: troubleshooting, the comparison, the final challenge, cleanup, and the summary."""

from __future__ import annotations

from components import arrow, box, card, checklist, grid, label, notes, svg, terminal, tile
from recordings import rec
from scenes_common import EKC, KAC, MIC, MKC, S, TS, scene

# ---------------------------------------------------------------- 14. Troubleshooting Kubernetes
scene("Troubleshooting Kubernetes", "troubleshooting/README", "The method, for every failure", checklist([
    (0, "1", "What exactly is the symptom?", "kubectl get nodes / pods -A: read the STATUS column"),
    (1, "2", "What does Kubernetes know?", "kubectl describe: Conditions and Events"),
    (2, "3", "What does the component say?", "kubectl logs --previous · journalctl -u kubelet / -u containerd"),
    (3, "4", "Which layer?", "network → runtime → kubelet → API server → workload configuration"),
    (4, "5", "Change one thing, then verify", "the command that showed the symptom must now show it fixed"),
]), [
    S("Five more labs, and one method for all of them. First, what exactly is the symptom? Read the status column."),
    S("Second, what does Kubernetes know about it? Describe the object, and read its conditions and events."),
    S("Third, what does the component itself say? Container logs, or the system journal of the kubelet and containerd."),
    S("Fourth, which layer is broken: the network, the runtime, the kubelet, the A P I server, or the workload's configuration?"),
    S("And fifth, change one thing, and verify with the same command that showed the problem."),
])

scene(None, "Recorded · troubleshooting/02", "Everything is green, and the network is broken", terminal(
    rec(TS[2], "kubectl get nodes", width=150, tones={"Ready": "ok"})
    + rec(TS[2], "curl -sS --max-time 5", step=1, nth=0, wrap=118, tones={"timed out": "bad"},
          cmd='POD_IP=...   # a web Pod on the worker\ncurl -sS --max-time 5 "http://$POD_IP"')
    + rec(TS[2], "sysctl net.ipv4.ip_forward", step=2, tones={"= 0": "bad"}),
    "bash (recorded)"), [
    S("Lab two is the nasty one. Every node is Ready, every Pod is Running. Nothing looks wrong."),
    S("But from the control plane, a Pod on the worker does not answer. The request times out.", zoom=1.25),
    S("The Pod answers inside itself, and Flannel's devices exist. So, the node in the middle: is it still forwarding "
      "packets? I P forward is zero. Someone switched it off. sysctl dash dash system restores the saved value, and the "
      "request works again. This is why we test traffic across nodes.", zoom=1.3),
])

scene(None, "Recorded · troubleshooting/05", "kubectl cannot connect", terminal(
    rec(TS[5], "KUBECONFIG=/tmp/does-not-exist kubectl get nodes", wrap=118, drop="memcache", tones={"localhost:8080": "bad"})
    + rec(TS[5], "kubectl --kubeconfig /tmp/broken-config get nodes", step=1, wrap=118, drop="memcache", tones={"Unable to connect": "bad"})
    + rec(TS[5], "kubectl config view --minify --kubeconfig /tmp/broken-config", step=2, width=150, tones={"10.255.255.1": "bad"}),
    "k8s-cp (recorded)"), [
    S("Lab five. The two most common kube control errors. localhost eight thousand eighty refused means kube control "
      "found no kube config at all.", zoom=1.2),
    S("A timeout to an address means the kube config points at the wrong server."),
    S("The first command when kube control misbehaves: config view dash dash minify. It shows exactly where kube control "
      "is going to connect."),
])

scene(None, "Recorded · troubleshooting/06", "CoreDNS in CrashLoopBackOff", terminal(
    rec(TS[6], "kubectl get pods -n kube-system -l k8s-app=kube-dns", nth=0, width=150, tones={"CrashLoopBackOff": "bad"})
    + rec(TS[6], "kubectl logs -n kube-system", step=1, wrap=118, tones={"forwardd": "bad"},
          cmd="kubectl logs -n kube-system $POD --previous --tail=5")
    + rec(TS[6], "nslookup web.default.svc.cluster.local", step=2, tones={"Address": "ok"}),
    "k8s-cp (recorded)"), [
    S("Lab six. Someone tidied up the Core D N S configuration. The new Core D N S Pods crash, again and again: crash loop back off."),
    S("Crash loop back off is not the cause, it only means the container keeps exiting. The cause is in the logs of the "
      "last crashed run: an unknown directive, forwardd, with two Ds. One typo.", zoom=1.25),
    S("Restore the backup, restart Core D N S, and a test Pod resolves the web Service's name again."),
])

scene(None, "Recorded · troubleshooting/07", "The container runtime is down", terminal(
    rec(TS[7], "kubectl describe node k8s-worker | grep", wrap=118, tones={"runtime": "bad"})
    + rec(TS[7], 'echo "kubelet $(systemctl is-active kubelet)"', step=1, tones={"inactive": "bad", "kubelet active": "ok"})
    + rec(TS[7], "sudo journalctl -u kubelet", step=2, wrap=118, tones={"containerd.sock": "bad"}),
    "bash (recorded)"), [
    S("Lab seven. The worker is Not Ready again. Same symptom as lab one, but read the message: this time the kubelet "
      "is reporting, and it reports a runtime problem."),
    S("On the node: the kubelet is active, containerd is inactive."),
    S("And the kubelet's journal shows it failing to reach containerd's socket. Start containerd, and the node is "
      "Ready. Same symptom, different layer: always read the message."),
])

# ---------------------------------------------------------------- 15. comparison
scene("Installation method comparison", "docs/13", "Four methods side by side", svg(
    label(0, 460, 40, "kubeadm", 30, "sky", "middle", 900) + label(0, 840, 40, "Minikube", 30, "ok", "middle", 900)
    + label(0, 1220, 40, "MicroK8s", 30, "amber", "middle", 900) + label(0, 1600, 40, "Amazon EKS", 30, "violet", "middle", 900)
    + "".join(label(1 + r // 3, 0, 120 + r * 82, name, 24, "#c9d6e6", "start", 800) for r, name in enumerate([
        "for", "control plane", "datastore", "default CNI", "high availability", "who upgrades", "cost", "production?"]))
    + "".join(label(1 + r // 3, 460 + c * 380, 120 + r * 82, v, 22, "#f1f6fc", "middle", 600)
              for r, row in enumerate([
                  ["learning, own servers", "laptop, CI", "edge, small servers", "production on AWS"],
                  ["static Pods, yours", "inside a container", "kubelite process", "AWS, invisible"],
                  ["etcd", "etcd", "dqlite", "etcd (AWS)"],
                  ["you choose (Flannel)", "built in", "Calico", "Amazon VPC CNI"],
                  ["3 CPs + load balancer", "no", "3+ nodes, automatic", "built in, multi-AZ"],
                  ["you, kubeadm upgrade", "minikube start", "snap channel", "AWS + you (nodes)"],
                  ["your hardware", "free", "free", "≈ $0.25–0.30 / hour"],
                  ["yes, if you operate it", "no", "edge / small", "yes"]])
              for c, v in enumerate(row))
), [
    S("Let's put the four side by side. kube admin is for learning and for running Kubernetes on your own servers. "
      "Minikube for laptops and C I. MicroK8s for edge devices and small servers. EKS for production on AWS."),
    S("The control plane: static Pods you own, a container, a single process, or invisible in AWS's account. "
      "The datastore: etcd everywhere except MicroK8s. And the network plugin: your choice, built in, Calico, or the "
      "V P C C N I."),
    S("High availability: three control planes and a load balancer with kube admin, none for Minikube, automatic "
      "with three MicroK8s nodes, and built in on EKS. Upgrades are yours, except the EKS control plane."),
    S("Cost and production use. Free locally. On EKS, about thirty cents per hour, and in return you operate much less."),
])

scene(None, "labs/05", "Which one should I use?", grid([
    card(0, "🧑‍💻", "Test a Helm chart on a laptop", "Minikube: one command, delete it after", "ok"),
    card(0, "🔁", "Integration tests on every pull request", "Minikube (or kind): a fresh cluster per run", "ok"),
    card(1, "🏭", "40 small industrial PCs, offline", "MicroK8s: one snap, add-ons, HA with 3 nodes", "amber"),
    card(1, "🚀", "Customer API on AWS, no Kubernetes team", "EKS: AWS runs the control plane", "violet"),
    card(2, "🏦", "Own data centre, full control", "kubeadm: you own every certificate and component", "blue"),
    card(2, "🎓", "Preparing for the CKA exam", "kubeadm: install, join, upgrade, back up etcd", "blue"),
], cols=2), [
    S("Lab five turns this into decisions. A developer testing a chart on a laptop, or a C I pipeline: Minikube."),
    S("A factory with forty small machines, often offline: MicroK8s. A start-up with a customer A P I on AWS and no "
      "Kubernetes specialist: EKS."),
    S("A bank that must own everything in its own data centre, or you, preparing for the C K A exam: kube admin. "
      "Most companies use two at once: a local cluster for development, and a managed one for production."),
])

# ---------------------------------------------------------------- 16. Final challenge
scene("Final challenge", "capstone/", "The Monday morning cluster", svg(
    box(0, 0, 20, 540, 230, "🔌", "fault 1", ["kubectl points at a server", "that does not exist"], "bad", "#2a1520")
    + box(0, 590, 20, 540, 230, "🛑", "fault 2", ["containerd stopped", "on the worker"], "bad", "#2a1520")
    + box(0, 1180, 20, 540, 230, "🚧", "fault 3", ["IP forwarding off", "on the worker"], "bad", "#2a1520")
    + label(1, 860, 330, "Find every fault from the symptoms. Fix the layer that hides the others first.", 30, "amber", "middle", 800)
    + label(2, 860, 410, "Then the full checklist: nodes, system Pods, DNS, NodePort, and Pod-to-Pod across nodes.", 30, "sky", "middle", 700)
    + label(3, 860, 490, "Finish with a 5–10 line incident note: what broke, impact, how found, how fixed, prevention.", 30, "ok", "middle", 700)
    + box(4, 360, 560, 1000, 140, "📝", "Plus 15 questions", ["architecture, runtime, CNI, kubeadm, EKS, cleanup, choosing a method"], "blue")
), [
    S("The capstone. On Monday morning, the team's kube admin cluster stopped working over the weekend. There are three "
      "faults at once: kube control points at the wrong server, containerd is stopped on the worker, and I P forwarding "
      "is off."),
    S("Find them from the symptoms, as if you didn't know. Hint: fix the layer that hides the others first. You cannot "
      "investigate nodes while kube control cannot even reach the A P I."),
    S("When the nodes look healthy, run the full checklist, including Pod to Pod traffic across nodes. That is where "
      "the third fault hides."),
    S("And finish like a professional: a short incident note. What broke, the impact, how you found it, how you fixed "
      "it, and how to prevent it."),
    S("The capstone also has fifteen questions. Answer them without notes. If you can, you have understood this course. "
      "The scenario is tested too: it runs in C I on the real cluster."),
])

# ---------------------------------------------------------------- 17. Cleanup
scene("Cleanup", "Recorded · kubeadm/cleanup.md", "Reset the kubeadm cluster", terminal(
    rec(KAC, "kubectl drain k8s-worker", tail=3, width=150, tones={"deleted": "ok"})
    + rec(KAC, "sudo kubeadm reset -f", step=1, nth=1, tail=3, width=150)
    + rec(KAC, "kubectl get nodes", step=2, wrap=118, drop="memcache", tones={"refused": "ok"}),
    "bash (recorded)"), [
    S("Time to clean up, and to prove it. kube admin first: drain the worker, so its Pods move away cleanly, and delete "
      "the node from the cluster."),
    S("kube admin reset on both machines removes the control plane, etcd's data and the certificates. It does not "
      "remove the C N I configuration and the I P tables rules: the lesson does that too."),
    S("Proof: the A P I server is gone, connection refused. Then multipass delete and purge remove the machines."),
])

scene(None, "Recorded · minikube/cleanup.md and microk8s/cleanup.md", "Minikube and MicroK8s", terminal(
    rec(MKC, "minikube delete", nth=0, tones={"Removed": "ok"})
    + rec(MKC, "docker ps -a --filter name=minikube", step=1, tones={"no Kubernetes containers left": "ok"})
    + rec(MIC, "sudo snap remove microk8s --purge", step=2, tones={"removed": "ok"})
    + rec(MIC, "multipass list", step=3),
    "bash (recorded)"), [
    S("Minikube: one command removes the container, its disk and its kube control context."),
    S("And we check: no Kubernetes containers left."),
    S("MicroK8s: snap remove with purge removes the package and all its data, without keeping a snapshot."),
    S("And the machine itself is deleted."),
])

scene(None, "Recorded · eks/cleanup.md", "EKS: the order matters", terminal(
    rec(EKC, "kubectl delete service web", tones={"deleted": "ok"})
    + rec(EKC, "eksctl delete cluster -f eks/cluster.yaml --wait", step=1, tail=3, width=150, tones={"all cluster resources were deleted": "ok"})
    + rec(EKC, "eks/scripts/verify-cleanup.sh", step=2, nth=1, tones={"gone": "ok", "Clean": "ok"}),
    "bash (recorded)"), [
    S("EKS, and here the order matters. First delete the LoadBalancer Service. The load balancer was created by "
      "Kubernetes, not by eksctl. If the cluster disappears first, the load balancer stays, keeps costing money, and "
      "blocks the deletion of the V P C."),
    S("Then eksctl delete cluster. Eleven minutes later, measured: all cluster resources were deleted."),
    S("Never trust it should be gone. The verification script checks every resource type: cluster, stacks, V P C, "
      "nat gateway, elastic I Ps, instances, volumes, load balancers, security groups and I A M roles. Clean.", zoom=1.15),
])

scene(None, "Recorded · the account, before and after", "Back to exactly where we started", grid([
    tile(0, "📋", "region inventory", "before = after", "ok", "EKS 0 · VPCs 1 · NAT 0 · EIPs 0 · LBs 0 · EC2 0"),
    tile(1, "⏱️", "cluster lifetime", "≈ 41 min", "blue", "create 14.5 min · test + console · delete 11 min"),
    tile(2, "💵", "cost of the lesson", "≈ $0.15–0.20", "amber", "on-demand list prices, Frankfurt"),
    tile(3, "🔐", "leftovers", "none", "ok", "no OIDC provider, log groups, ENIs or volumes"),
], cols=4), [
    S("And the final check: the inventory of the region after cleanup is identical to the one before we started."),
    S("The cluster existed for about forty-one minutes: fourteen and a half to create, our tests and the console tour, "
      "and eleven minutes to delete."),
    S("At on-demand list prices, the whole EKS lesson cost roughly fifteen to twenty cents."),
    S("Nothing was left behind. That is what responsible cloud work looks like."),
])

# ---------------------------------------------------------------- 18. Final summary
scene("Final summary", "What you can do now", "From \"never installed Kubernetes\" to this", checklist([
    (0, "✓", "Explain the architecture", "control plane, nodes, add-ons, and what happens on kubectl apply"),
    (1, "✓", "Install Kubernetes four ways", "kubeadm by hand, Minikube, MicroK8s and Amazon EKS"),
    (2, "✓", "Verify any cluster", "the same checklist: nodes, system Pods, API health, workload, Service, cross-node traffic"),
    (3, "✓", "Troubleshoot installation problems", "NotReady, Pod network, init, join, kubeconfig, CoreDNS, runtime, resources"),
    (4, "✓", "Choose and clean up", "the right method for a situation, and no leftovers, especially in the cloud"),
]), [
    S("Let's look back. You started with: I have never installed Kubernetes. Now you can explain the architecture, "
      "and what happens when you run kube control apply."),
    S("You have installed Kubernetes four ways: by hand with kube admin, with Minikube, with MicroK8s, and on Amazon EKS."),
    S("You can verify any cluster with one checklist, including the test most people forget: traffic across nodes."),
    S("You have found and fixed eight real installation problems, always with the same method."),
    S("And you know which method to choose, and how to leave nothing behind."),
])

scene(None, "Your next steps", "Understand → Install → Verify → Break → Troubleshoot → Compare → Repeat", grid([
    card(0, "🧭", "Follow the tutorial", "tutorial/ walks the repository chapter by chapter", "blue"),
    card(0, "🛠️", "Build it yourself", "every lesson runs on your computer; the outputs show what to expect", "ok"),
    card(1, "🎯", "Do the labs and the capstone", "solutions are hidden: try first", "amber"),
    card(1, "📚", "Study", "glossary, 25 interview questions, the knowledge check", "violet"),
], cols=2), [
    S("Your next steps. Follow the tutorial folder, and build every cluster yourself. The outputs in the lessons show "
      "you exactly what to expect."),
    S("Do the labs and the capstone before you open the solutions. Then repeat: understand, install, verify, break, "
      "troubleshoot, compare. Thanks for watching, and happy building."),
])
