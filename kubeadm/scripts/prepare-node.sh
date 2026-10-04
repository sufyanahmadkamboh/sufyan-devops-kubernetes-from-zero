#!/usr/bin/env bash
# Prepares an Ubuntu 24.04 machine as a kubeadm node: exactly steps 2-4 of kubeadm/README.md
# (swap off, kernel modules, sysctl, containerd 2.x with systemd cgroups, kubelet/kubeadm/kubectl held at v1.37).
#
# Run it on the new machine, as a user with sudo, for example from your computer:
#   multipass exec k8s-worker2 -- bash -s < kubeadm/scripts/prepare-node.sh
#
# CONFIGURE_CONTAINERD=no skips the containerd configuration step. Only troubleshooting/03 uses it, to reproduce a
# common mistake on purpose.
set -euo pipefail
K8S_MINOR="${K8S_MINOR:-v1.37}"
CONFIGURE_CONTAINERD="${CONFIGURE_CONTAINERD:-yes}"
export DEBIAN_FRONTEND=noninteractive

echo "==> swap off"
sudo swapoff -a
sudo sed -i '/\sswap\s/ s/^/#/' /etc/fstab

echo "==> kernel modules and sysctl"
printf 'overlay\nbr_netfilter\n' | sudo tee /etc/modules-load.d/k8s.conf > /dev/null
sudo modprobe overlay
sudo modprobe br_netfilter
printf 'net.ipv4.ip_forward = 1\nnet.bridge.bridge-nf-call-iptables = 1\nnet.bridge.bridge-nf-call-ip6tables = 1\n' \
  | sudo tee /etc/sysctl.d/k8s.conf > /dev/null
sudo sysctl --system > /dev/null

echo "==> containerd (Docker's apt repository)"
sudo apt-get update -q
sudo apt-get install -y -q ca-certificates curl gpg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor --yes -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update -q
sudo apt-get install -y -q containerd.io
if [ "$CONFIGURE_CONTAINERD" = yes ]; then
  containerd config default | sudo tee /etc/containerd/config.toml > /dev/null
  sudo sed -i 's/SystemdCgroup = false/SystemdCgroup = true/' /etc/containerd/config.toml
  sudo systemctl restart containerd
else
  echo "    (skipping the containerd configuration on purpose)"
fi

echo "==> kubelet, kubeadm, kubectl $K8S_MINOR"
curl -fsSL "https://pkgs.k8s.io/core:/stable:/$K8S_MINOR/deb/Release.key" | sudo gpg --dearmor --yes -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
echo "deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/$K8S_MINOR/deb/ /" \
  | sudo tee /etc/apt/sources.list.d/kubernetes.list > /dev/null
sudo apt-get update -q
sudo apt-get install -y -q kubelet kubeadm kubectl cri-tools
sudo apt-mark hold kubelet kubeadm kubectl > /dev/null
sudo systemctl enable --now kubelet

echo "==> ready: $(hostname), $(containerd --version | awk '{print $3}'), kubeadm $(kubeadm version -o short)"
