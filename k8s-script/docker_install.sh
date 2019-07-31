#!/usr/bin

if [ -d /data/k8s/script ]; then
    cd /data/k8s/script
else
    mkdir -pv /data/k8s/script
    cd /data/k8s/script
fi

set -xv
exec 1>docker.log 2>&1

# 创建/data/k8s/script目录
echo "创建/data/k8s/script目录"


# 开始安装docker-ce版本
echo "starting install docker-ce"
#sudo yum install -y net-tools yum-utils device-mapper-persistent-data lvm2
sed -i 's%#!/usr/bin/python%#!/usr/bin/python2%' /bin/yum-config-manager 
sudo yum-config-manager --add-repo http://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
sudo yum makecache fast
sudo yum -y install docker-ce
sudo systemctl enable docker
systemctl start docker

# 更改docker 仓库
echo "编辑/etc/docker/daemon.json" 
cat << EOF > /etc/docker/daemon.json
{
  "registry-mirrors": ["http://hub-mirror.c.163.com"]
}
EOF

# 关闭firewalld
echo "停止firewalld"
systemctl stop firewalld
systemctl disable firewalld

# 关闭selinux
echo "关闭selinux"
setenforce 0 && sed -i 's/^SELINUX=enforcing$/SELINUX=permissive/' /etc/selinux/config

#关闭swapof
echo "关闭swapoff"
swapoff -a
sed -i 's%/dev/mapper/centos-swap%#/dev/mapper/centos-swap%' /etc/fstab

reboot
