# Kubernetes From Zero · project summary

**What:** a hands-on Kubernetes installation lab for beginners. You install Kubernetes four ways (kubeadm, Minikube,
MicroK8s, Amazon EKS), verify each cluster with the same checklist, break it on purpose, fix it, compare the methods and
clean everything up.

**Problem:** beginners copy install commands without knowing why each prerequisite exists, panic at the normal
NotReady state after `kubeadm init`, never practise failures before they meet them at work, and can leave cloud
resources running that keep billing.

**Contents**
- 13 concept lessons (`docs/`), four installation lessons with cleanup pages, a ten-level roadmap, a 12-chapter guided
  tutorial (`tutorial/`)
- 8 troubleshooting labs (`troubleshooting/`): NotReady node, Pod networking, kubeadm init failure, worker join failure,
  kubectl connection, CoreDNS CrashLoopBackOff, container runtime down, insufficient resources
- 5 challenges with hidden solutions (`labs/`), a capstone with 15 questions and a three-fault incident scenario
- Study guide PDF (63 pages), glossary, 25 interview questions, an 18-chapter video (full and silent versions)

**Engineering details**
- `tests/mdrun.py` runs every bash block of the lessons on the right machine (control plane, worker, host) and writes the
  real output back into the docs; GitHub Actions creates Ubuntu 24.04 VMs with LXD (a small Multipass-compatible shim)
  and runs the kubeadm, Minikube and MicroK8s lessons, the troubleshooting labs and the capstone on every change
- Versions: Kubernetes 1.37, containerd 2 with the systemd cgroup driver, Flannel v0.28.9, Minikube v1.39.0,
  MicroK8s 1.36/stable, EKS 1.37 with eksctl v0.231.0
- EKS run (lab, eu-central-1): create 868.9 s, delete 674.9 s, cluster lifetime about 41 min, region inventory after
  cleanup identical to before, cost roughly $0.15–0.20 at on-demand list prices; 22 console screenshots from a
  read-only session, each OCR-checked before use

**Tech:** Kubernetes, kubeadm, containerd, Flannel, Minikube, MicroK8s, Amazon EKS, eksctl, AWS CLI, Multipass, LXD,
Bash, Python, GitHub Actions.

**Links:** https://github.com/sufyanahmadkamboh/sufyan-devops-kubernetes-from-zero · https://sufyanahmadkamboh.github.io/
