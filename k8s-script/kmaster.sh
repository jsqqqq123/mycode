#!/usr/bin
if [ -d /data/k8s/script ]; then
    cd /data/k8s/script
else
    mkdir -pv /data/k8s/script
    cd /data/k8s/script
fi

set -xv
exec 1>kmaster.log 2>&1

echo "编辑/etc/yum.repos.d/kubernetes.repo"
#添加kubernetes.repo
cat <<EOF > /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=https://mirrors.aliyun.com/kubernetes/yum/repos/kubernetes-el7-x86_64
enabled=1
gpgcheck=1
repo_gpgcheck=1
gpgkey=https://mirrors.aliyun.com/kubernetes/yum/doc/yum-key.gpg https://mirrors.aliyun.com/kubernetes/yum/doc/rpm-package-key.gpg
EOF

echo "编辑/etc/sysctl.d/k8s.conf"
cat <<EOF > /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
EOF
sysctl -p /etc/sysctl.d/k8s.conf

# 以下是安装k8s
echo "install k8s"
yum install -y kubelet kubeadm kubectl --disableexcludes=kubernetes

# 设置k8s镜像国内拉取

echo "设置kubernetes version  image-repository 镜像为国内 pod network"
sudo kubeadm init --image-repository registry.aliyuncs.com/google_containers --kubernetes-version v1.15.0 --pod-network-cidr=10.244.0.0/16 >> joinToken.log

echo "start kubelet.service"
systemctl enable kubelet.service
systemctl start kubelet.service
