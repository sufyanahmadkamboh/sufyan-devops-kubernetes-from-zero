"""Shared helpers for the scene scripts (scenes_1_intro.py ... scenes_5_finish.py, collected by scenes.py)."""

from __future__ import annotations

SCENES: list[dict] = []


def S(say: str, hl: tuple[int, int] | None = None, tts: str | None = None, zoom: float = 1) -> dict:
    """One narration step. zoom > 1 moves the camera into the terminal, centred on the lines this step reveals."""
    return {"say": say, "hl": hl, "tts": tts, "zoom": zoom}


def shot(s: int, src: str, alt: str, style: str = "height:700px;width:auto") -> str:
    return f'<img class="shot st" data-s="{s}" src="../assets/{src}" alt="{alt}" style="{style}">'


def scene(chapter, kicker, title, body, steps, layout="full"):
    SCENES.append({"chapter": chapter, "kicker": kicker, "title": title, "body": body, "steps": steps, "layout": layout})


# lesson files whose recordings the terminals show
KA, KAC = "kubeadm/README.md", "kubeadm/cleanup.md"
MK, MKC = "minikube/README.md", "minikube/cleanup.md"
MI, MIC = "microk8s/README.md", "microk8s/cleanup.md"
EK, EKC = "eks/README.md", "eks/cleanup.md"
TS = {n: f"troubleshooting/{n:02d}-{name}.md" for n, name in [
    (1, "node-not-ready"), (2, "pod-networking"), (3, "kubeadm-init-failure"), (4, "worker-join-failure"),
    (5, "kubectl-connection"), (6, "core-pods-not-running"), (7, "container-runtime"), (8, "insufficient-resources")]}
LAB = {1: "labs/01-kubeadm-installation.md", 2: "labs/02-minikube-installation.md", 3: "labs/03-microk8s-installation.md"}
EX = "examples/nginx/README.md"
