Most Kubernetes install guides end with "your cluster is ready". Then a node says NotReady, a Pod stays Pending, or a cloud bill shows up, and you are on your own. So I built a free lab where you install Kubernetes four ways, break it on purpose, and learn to fix it. ☸️👇

Think of it as learning to drive four vehicles. kubeadm is a car you build from parts: you see every piece. Minikube is the driving simulator on your laptop. MicroK8s is a scooter: small, starts at once. Amazon EKS is a taxi: someone else maintains the engine, and the meter is running.

That is "Kubernetes From Zero":

🛠️ kubeadm: a real 2-node cluster on Ubuntu 24.04, built by hand (containerd 2, Flannel), every prerequisite explained
💻 Minikube: a complete cluster inside one container, profiles, two Kubernetes versions side by side
📦 MicroK8s: one snap, kubelite and dqlite, an Ingress with Traefik
☁️ Amazon EKS: eksctl, the AWS Console path (what to click), a real load balancer, and a verified teardown

The same verification checklist runs on every cluster, and 8 troubleshooting labs reproduce the errors you will meet at work:
⛔ NetworkPluginNotReady: cni plugin not initialized
⛔ Kubelet stopped posting node status
⛔ 0/1 nodes are available: Insufficient cpu
⛔ CrashLoopBackOff from a one-letter typo in CoreDNS ("forwardd")
⛔ The connection to the server localhost:8080 was refused

Each one: symptom → investigation → root cause → fix → verification. No guessing.

Two things I am proud of:
✅ Every command in the kubeadm, Minikube and MicroK8s lessons runs automatically on fresh virtual machines in GitHub Actions, and the output in the docs is the real output.
✅ The EKS lesson ran against a real AWS account: created in 14.5 minutes, tested, deleted in 11, and the region inventory afterwards was identical to before. The whole run cost roughly $0.15–0.20 at list prices.

Study material included: 13 concept lessons, a 12-chapter guided tutorial, 5 challenges, a capstone (15 questions + an incident scenario), an 18-chapter video, a 63-page PDF study guide, a glossary and 25 interview questions.

🔗 Repository: https://github.com/sufyanahmadkamboh/sufyan-devops-kubernetes-from-zero
🌐 All my projects: https://sufyanahmadkamboh.github.io/

Which install method do you use at work, and why? 💬

#Kubernetes #DevOps #CloudNative #AWS #EKS #kubeadm #LearningDevOps #OpenSource
