"""Kubernetes From Zero: the video course, 18 chapters.

Every terminal shows real output: the kubeadm, Minikube and MicroK8s lessons and the troubleshooting labs were recorded
while CI ran them on fresh virtual machines (tests/mdrun.py --record), the EKS lesson while it ran against AWS.
The console screenshots come from a read-only AWS Console session during the same EKS run (eks/console/).
The chapters are split over five modules; this one collects them and adds the production layer.
"""

from __future__ import annotations

import scenes_1_intro  # noqa: F401  (chapters 1-4)
import scenes_2_kubeadm  # noqa: F401  (chapters 5-7)
import scenes_3_local  # noqa: F401  (chapters 8-11)
import scenes_4_eks  # noqa: F401  (chapters 12-13)
import scenes_5_finish  # noqa: F401  (chapters 14-18)
from production import package
from scenes_common import SCENES

package(SCENES, "Install it 4 ways · verify · break · fix · compare",
        ["kubeadm", "Minikube", "MicroK8s", "Amazon EKS"], {
    "Ready? Not yet.": {0: "error", 1: "error"},
    "Install Flannel → Ready": {1: "success"},
    "Join the worker": {1: "success"},
    "From the control plane to a Pod on the worker": {0: "success"},
    "A node is NotReady": {0: "error", 2: "success"},
    "kubeadm init fails at preflight": {0: "error", 3: "success"},
    "A worker cannot join": {2: "error"},
    "When the laptop is too small": {0: "error", 2: "error", 3: "success"},
    "Workload, NodePort, Ingress": {2: "success", 3: "error"},
    "eksctl create cluster": {1: "success"},
    "A real load balancer in front of the app": {2: "success"},
    "Everything is green, and the network is broken": {1: "error", 2: "success"},
    "kubectl cannot connect": {0: "error"},
    "CoreDNS in CrashLoopBackOff": {0: "error", 2: "success"},
    "The container runtime is down": {0: "error"},
    "EKS: the order matters": {2: "success"},
    "Back to exactly where we started": {0: "success"},
})

assert len([s for s in SCENES if s["chapter"]]) == 18, "the course has exactly 18 chapters"
