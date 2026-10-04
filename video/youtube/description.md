Kubernetes From Zero: install Kubernetes four ways and understand every step. We build a real two-node cluster by hand with kubeadm on Ubuntu 24.04 (containerd 2, Flannel), then Minikube on a laptop, MicroK8s from one snap, and a managed cluster on Amazon EKS with eksctl, including the AWS Console path, a load balancer, and a verified teardown back to the exact starting state. Every cluster gets the same verification checklist, and eight troubleshooting labs break things on purpose: NotReady nodes, Pod networking, kubeadm init and join failures, kubeconfig errors, CoreDNS crashes, a dead container runtime, and insufficient resources. Every terminal shows real output recorded while the lessons ran on fresh virtual machines.

💻 The lab (free, open source): https://github.com/sufyanahmadkamboh/sufyan-devops-kubernetes-from-zero
🌐 All my projects: https://sufyanahmadkamboh.github.io/

🧪 Do it yourself:
1. git clone https://github.com/sufyanahmadkamboh/sufyan-devops-kubernetes-from-zero.git
2. Open tutorial/00-start-here.md and follow the roadmap (Levels 1–10)
3. Break the clusters with the troubleshooting labs, then take the capstone

⏱️ Chapters
0:00 Introduction
1:51 What Kubernetes is
3:10 Kubernetes architecture
5:35 Prerequisites
7:42 A full cluster with kubeadm
10:51 Verify the kubeadm cluster
12:01 Troubleshoot kubeadm
14:01 Minikube installation
15:00 Minikube verification
16:45 MicroK8s installation
17:51 MicroK8s verification
18:46 Amazon EKS setup
22:58 EKS verification
24:59 Troubleshooting Kubernetes
27:41 Installation method comparison
29:14 Final challenge
30:13 Cleanup
32:17 Final summary

📊 What you will see (all recorded)
• kubeadm init, the NotReady surprise (cni plugin not initialized), Flannel, kubeadm join
• the verification checklist: readyz, a test workload, NodePort, Pod-to-Pod across nodes
• Minikube: a node inside one container; profiles; "Insufficient cpu"
• MicroK8s: kubelite and dqlite, add-ons, an Ingress with Traefik
• Amazon EKS: what to click in the console, eksctl create (14.5 min), the VPC CNI, a load balancer, cleanup in the right order and a region inventory identical to the start

#Kubernetes #DevOps #CloudNative
