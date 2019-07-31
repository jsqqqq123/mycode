#!/usr/bin

if [ -d /data/k8s/script ]; then
    cd /data/k8s/script
else
    mkdir -pv /data/k8s/script
    cd /data/k8s/script
fi

set -xv
exec 1>knode.log 2>&1

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

echo "install k8s"
yum install -y kubelet kubeadm kubectl --disableexcludes=kubernetes

echo "docker pull k8s required images"
docker pull mirrorgooglecontainers/kube-proxy:v1.15.0
docker tag docker.io/mirrorgooglecontainers/kube-proxy:v1.15.0 k8s.gcr.io/kube-proxy:v1.15.0

docker pull mirrorgooglecontainers/pause:3.1
docker tag docker.io/mirrorgooglecontainers/pause:3.1 k8s.gcr.io/pause:3.1

echo "starting kubelet.service "
systemctl enable kubelet.service
systemctl start kubelet.service
