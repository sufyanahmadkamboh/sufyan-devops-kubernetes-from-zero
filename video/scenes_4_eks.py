"""Chapters 12-13: Amazon EKS setup (eksctl and the console path) and its verification."""

from __future__ import annotations

from pathlib import Path

from components import arrow, box, card, code, grid, label, notes, svg, terminal, tile
from recordings import rec
from scenes_common import EK, S, scene

CONSOLE = "../../eks/console/"


def screens(items: list[tuple[int, str, int]], w: int = 1500, h: int = 700) -> str:
    """Console screenshots stacked in one frame; each step reveals the next one on top. (step, file, y-offset)."""
    out = "".join(
        f'<div class="st" data-s="{s}" style="position:absolute;inset:0;border-radius:16px;border:3px solid #284468;'
        f'box-shadow:0 20px 60px rgba(0,0,0,.5);background:#fff url({CONSOLE}{src}) no-repeat 0 -{y}px / {w}px auto"></div>'
        for s, src, y in items)
    return f'<div style="position:relative;width:{w}px;height:{h}px">{out}</div>'


_YAML = (Path(__file__).resolve().parent.parent / "eks" / "cluster.yaml").read_text(encoding="utf-8")
# an excerpt that fits on one screen at a readable size: no comments (the notes beside it explain them), no blank
# lines, and without the node group's labels and tags (everything up to privateNetworking is shown)
_SHOWN = [x.split(" #")[0].rstrip() for x in ("apiVersion:" + _YAML.split("apiVersion:", 1)[1]).splitlines()
          if x.strip() and not x.lstrip().startswith("#")]
CLUSTER_YAML = "\n".join(_SHOWN[:next(i for i, x in enumerate(_SHOWN) if "privateNetworking" in x) + 1])


def lines(first: str, last: str) -> tuple[int, int]:
    """1-based line range of the shown YAML from the line starting with `first` to the one starting with `last`."""
    ys = [x.strip() for x in CLUSTER_YAML.splitlines()]
    a = next(i for i, x in enumerate(ys, 1) if x.startswith(first))
    return a, next(i for i, x in enumerate(ys, 1) if i >= a and x.startswith(last))

# ---------------------------------------------------------------- 12. Amazon EKS setup
scene("Amazon EKS setup", "docs/10", "Who runs what on EKS", svg(
    '<rect class="st" data-s="0" x="0" y="0" width="820" height="640" rx="26" fill="#221a3a" stroke="#b48cff" stroke-width="3"/>'
    + label(0, 30, 50, "AWS RUNS (in an AWS-owned account)", 26, "violet")
    + box(0, 30, 80, 760, 160, "🧠", "the control plane", ["API servers + etcd in several availability zones", "scaled, patched, backed up by AWS"], "violet", "#221a3a")
    + box(1, 30, 270, 760, 150, "💵", "about $0.10 per hour", ["for the control plane, whether you use it or not"], "amber", "#2b2410")
    + '<rect class="st" data-s="2" x="900" y="0" width="820" height="640" rx="26" fill="#0f2a22" stroke="#4cc286" stroke-width="3"/>'
    + label(2, 930, 50, "YOU RUN (in your account)", 26, "ok")
    + box(2, 930, 80, 760, 150, "🌐", "the VPC", ["subnets in 3 zones, NAT gateway, security groups"], "ok", "#0f2a22")
    + box(3, 930, 250, 760, 150, "🖥️", "the worker nodes", ["a managed node group: 2 × t3.medium EC2 instances"], "ok", "#0f2a22")
    + box(4, 930, 420, 760, 180, "🔑", "IAM and access", ["cluster role, node role, access entries", "(who may do what inside the cluster)"], "ok", "#0f2a22")
), [
    S("Now the cloud. On Amazon EKS, AWS runs the control plane for you, in its own account. The A P I servers and "
      "etcd run in several availability zones, and AWS keeps them patched, scaled and backed up."),
    S("That has a price: about ten cents per hour for the control plane alone, whether you use it or not."),
    S("Everything else is yours, in your account: the network, the V P C with subnets in three zones and a nat gateway,"),
    S("the worker nodes, here a managed node group of two E C2 instances,"),
    S("and I A M: which roles the cluster and the nodes use, and which people may do what inside the cluster."),
])

scene(None, "eks/README · before you create anything", "Cost and safety first", grid([
    tile(0, "💵", "while it runs", "$0.25–0.30/h", "amber", "control plane + 2 nodes + NAT + load balancer"),
    tile(1, "🌍", "one region only", "eu-central-1", "blue", "everything from one file, tagged"),
    tile(2, "📋", "inventory", "before = after", "ok", "inventory.sh counts what exists, twice"),
    tile(3, "🧹", "verified teardown", "nothing left", "ok", "verify-cleanup.sh checks every resource"),
], cols=4), [
    S("Before we create anything in the cloud, four rules. It costs money while it exists: about twenty-five to thirty "
      "cents per hour for this lab. Cheap for an afternoon, around two hundred dollars a month if forgotten."),
    S("Everything is created in one region, from one file, and tagged with the project name."),
    S("We count what exists in the region before we start, and again after cleanup. The numbers must match."),
    S("And the teardown is verified by a script that checks every resource type. It is part of the lesson, not an afterthought."),
])

scene(None, "Recorded · EKS lesson, step 2", "Who am I, and what is already there?", terminal(
    rec(EK, "aws sts get-caller-identity", tones={"arn:aws": "ok"})
    + rec(EK, "eks/scripts/inventory.sh", step=1),
    "bash (recorded)"), [
    S("First: which identity and which region are we using? The account number and the user name are masked in "
      "everything you see."),
    S("Then the inventory of the region, before we start. No EKS clusters, one V P C, no nat gateways, no load "
      "balancers, no instances. Keep these numbers in mind.", zoom=1.2),
])

scene(None, "eks/cluster.yaml", "The whole cluster, in one file", code("eks/cluster.yaml (excerpt)", CLUSTER_YAML, "yaml", 16) + notes([
    (0, "Where and which version", "region eu-central-1, Kubernetes 1.37, tags on everything"),
    (1, "The network", "a new VPC 10.50.0.0/16, one NAT gateway, endpoint public + private"),
    (2, "Access", "EKS API access entries: the creator becomes cluster-admin"),
    (3, "The nodes", "2 × t3.medium, 20 GB gp3, private subnets only"),
]), [
    S("This is the whole cluster, in one file for eksctl, the official command-line tool for EKS. The name, the region, "
      "version 1.37, and tags on everything.", hl=lines("apiVersion", "ManagedBy")),
    S("A new V P C with its own address range, and a single nat gateway, enough for a lab. The A P I endpoint is public, "
      "for our kube control, and private, for the nodes.", hl=lines("vpc:", "privateAccess")),
    S("Access entries decide who may use the cluster. The creator automatically becomes cluster admin.", hl=lines("accessConfig", "authenticationMode")),
    S("And the node group: two T3 medium instances with twenty gigabyte disks, in private subnets, with no public I P.",
      hl=lines("managedNodeGroups", "privateNetworking")),
], layout="code")

scene(None, "Recorded · AWS Console, read-only session", "The same thing in the console: what to click (1/3)", screens([
    (0, "01-clusters-create-cluster.webp", 0),
    (1, "02-custom-configuration.webp", 0),
    (2, "03-auto-mode-off.webp", 0),
]), [
    S("Before we run eksctl, let's see the console path, recorded live in a read-only session. In Elastic Kubernetes "
      "Service, clusters, click create cluster."),
    S("Choose custom configuration. Quick configuration would create an EKS Auto Mode cluster, where AWS also manages the nodes."),
    S("Auto Mode is on by default. Switch it off: we want the classic setup with a managed node group that we size ourselves."),
])

scene(None, "Recorded · AWS Console, read-only session", "The same thing in the console: what to click (2/3)", screens([
    (0, "04-name-and-iam-role.webp", 0),
    (1, "05-kubernetes-version.webp", 0),
    (2, "06-cluster-access.webp", 0),
]), [
    S("Enter the name, and choose the cluster I A M role, the role EKS uses to manage AWS resources for you. Create "
      "new role opens I A M with the right policy."),
    S("The console pre-selects version 1.36. Open the list and pick 1.37. Each version shows when its standard and "
      "extended support end."),
    S("Cluster access: allow cluster administrator access for your own identity, and the EKS A P I authentication mode."),
])

scene(None, "Recorded · AWS Console, read-only session", "The same thing in the console: what to click (3/3)", screens([
    (0, "08-networking.webp", 0),
    (1, "10-add-ons.webp", 0),
    (2, "13-review-create-button.webp", 0),
]), [
    S("Next, networking: a V P C, and subnets in at least two availability zones. The console pre-selects the default "
      "V P C. eksctl builds a dedicated one instead."),
    S("Then add-ons. The essential ones are the V P C C N I, Core D N S and kube-proxy."),
    S("And at the end of the review, the create button. We do not click it. Ours is created from the file, so it can "
      "be reviewed, repeated, and deleted with one command."),
])

scene(None, "Recorded · EKS lesson, step 5", "eksctl create cluster", terminal(
    rec(EK, "eksctl create cluster -f eks/cluster.yaml", nth=1, head=6, width=150)
    + [x for x in rec(EK, "eksctl create cluster -f eks/cluster.yaml", nth=1, step=1, tail=4, width=150,
                      tones={"is ready": "ok", "created 1 managed": "ok"}) if x[2] != "cmd"],
    "bash (recorded)"), [
    S("Now for real. eksctl create cluster dash f cluster dot yammel. It turns the file into two CloudFormation stacks: "
      "one for the cluster and its network, one for the node group."),
    S("Fourteen and a half minutes later, measured: two nodes ready, and the cluster k8s from zero is ready.", zoom=1.25),
])

# ---------------------------------------------------------------- 13. EKS verification
scene("EKS verification", "Recorded · the checklist, on EKS", "Control plane, nodes, system Pods", terminal(
    rec(EK, "aws eks describe-cluster", tones={"ACTIVE": "ok"})
    + rec(EK, "kubectl get nodes -o wide", step=1, width=150, tones={" Ready": "ok"})
    + rec(EK, "kubectl get pods -A", step=2, width=150, tones={"aws-node": "warn"}),
    "bash (recorded)"), [
    S("The same checklist, on EKS. The control plane is active, version 1.37, platform version e k s four."),
    S("Two worker nodes, Ready, Amazon Linux 2023 with containerd. Notice the I P addresses: ten fifty, from our V P C."),
    S("And the system Pods. No A P I server, no etcd: those run in AWS's account. Instead, aws-node: the Amazon V P C "
      "C N I, which gives Pods real V P C addresses. No overlay network like Flannel."),
])

scene(None, "Recorded · EKS lesson, step 7", "A real load balancer in front of the app", terminal(
    rec(EK, "kubectl get pods -l app=web -o wide", width=150, drop="successfully", cmd="kubectl get pods -l app=web -o wide")
    + rec(EK, "kubectl get service web", step=1, width=150, tones={"elb.amazonaws.com": "ok"})
    + rec(EK, "LB=$(kubectl get service web", step=2, tones={"Welcome to nginx": "ok"}),
    "bash (recorded)"), [
    S("Our web Deployment: two Pods on two nodes, with V P C addresses."),
    S("This time the Service is of type LoadBalancer. Kubernetes asks AWS for a real load balancer, and gives us its D N S name."),
    S("From the internet, through the AWS load balancer, to a node port, to a Pod: welcome to engine x.", zoom=1.3),
])

scene(None, "Recorded · AWS Console, read-only session", "The cluster, in the console", screens([
    (0, "21-cluster-overview.webp", 0),
    (1, "22-compute.webp", 0),
    (2, "26-access.webp", 0),
], h=740), [
    S("The same cluster in the console: active, version 1.37, its A P I endpoint and the I A M role eksctl created."),
    S("The compute tab shows the node group. But the node list says unauthorized! Our console session is read-only "
      "and has no EKS access entry. The console reads nodes through the Kubernetes A P I, and Kubernetes refuses it. "
      "An AWS permission alone does not let you inside the cluster."),
    S("The access tab shows who does have entries: the node role, an AWS service role, and our admin identity."),
])

scene(None, "Recorded · AWS Console, read-only session", "Everything it created around the cluster", screens([
    (0, "27-cloudformation-stacks.webp", 0),
    (1, "28-ec2-instances.webp", 0),
    (2, "29-load-balancer.webp", 0),
], h=640), [
    S("Outside EKS, CloudFormation shows the two stacks eksctl created."),
    S("E C2 shows the two worker instances, in two different availability zones."),
    S("And the load balancer that Kubernetes created for our Service. Remember it: it is not part of eksctl's stacks, "
      "and that matters when we delete everything."),
])
