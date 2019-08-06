# MyDocker 安装跟学习

## docker的安装


1 如果安装过docker 请移除相应的版本

```bash
[root@localhost ~]# sudo yum remove docker \
                  docker-client \
                  docker-client-latest \
                  docker-common \
                  docker-latest \
                  docker-latest-logrotate \
                  docker-logrotate \
                  docker-selinux \
                  docker-engine-selinux \
                  docker-engine
```

2 安装必要工具

```bash
[root@localhost ~]# sudo yum install -y yum-utils device-mapper-persistent-data lvm2

```

3 开始安装
```bash
[root@localhost ~]# sudo yum makecache fast

[root@localhost ~]# sudo yum -y install docker-ce

[root@localhost ~]# sudo systemctl start docker
```


## docker的基础命令

1. 查看运行中的container

```
[root@localhost ~]# docker ps    // docker ps -a  可以查看所有的无论运行没运行的. 也就是历史记录

```
2. 查看iamges

```
[root@localhost ~]# docker images

```


## docker 自建registry

1. 下载registry镜像

``` bash
[root@localhost ~]# docker pull registry

```

2. 如果有外部认证的ca证书最好, 如果没有请生成ca证书

``` bash
[root@localhost ~]# openssl req -newkey rsa:2048 -nodes -sha256 -keyout domain.key -x509 -days 365 -out domain.crt

```

3. 运行docker registry 其中加载目录根据实际情况来
``` bash
[root@localhost ~]#  docker run -d -p 5000:5000 --restart=always --name=registry -v /home/data/registry:/var/lib/registry -v /home/data/ssl/dockerssl:/data/certs -e REGISTRY_HTTP_TLS_CERTIFICATE=/data/certs/domain.crt -e REGISTRY_HTTP_TLS_KEY=/data/certs/domain.key registry

```

ps: 运行好后, 切勿在用docker run 来登录验证 以为那会重启再启动一个registry的 跟之前的不一样 可以用docker exec -it containerid command 的方式来输出命令

4. docker tag 将原本的image tag 变更
```
[root@localhost ~]# docker tag python:3.7 myregistry.com:5000/myregistry/python:3.7  */这里只是举个例子

```

5. 由于以上使用的证书的方式访问registry 所以需要在docker client端 也更新使用cert的方式 
```
[root@localhost ~]# mkdir -pv /etc/docker/certs.d/myregistry.com:5000    */ registry.com:5000 这个根据上面的docker tag的时候来操作 要匹配
[root@localhost ~]# cp domain.crt /etc/docker/certs.d/myregistry.com:5000/ca.crt  */ 记得要变成ca.crt
[root@localhost ~]# systemctl restart docker    */ 记得要重启docker
```

6. 用ip的方式 也就是 insecure-registry 的方式centos7的情况下 修改文件`/usr/lib/systemd/system/docker.service `中的ExecStart 这行添加 `--insecure-registry 10.10.105.71:5000`  如果是ubantu 则修改 `/etc/default/docker`中的 `DOCKER_OPTS`

ps: centos 更改docker daemon 的路径是 /usr/lib/systemd/system/docker.service中的ExecStart  ubantu 是 /etc/default/docker


## docker 命令解析

docker 运行镜像的命令
```
docker run --name somenginx02 --restart=always -v /opt/html:/usr/share/nginx/html -p 8181:80 -d nginx

--restart=always : 表示自动重启
-d nginx： 这里的nginx是要实在存在的镜像的名字 也可以用nginx:laste 来区分不同版本的nginx镜像
--name somenginx02 ： somenginx02 表示这个docker 启动的应用的标识 这个可以随意取，不过一般根据实际应用来取名字
```

docker 取消 --restart=always的办法
```
docker update --restart=no [container]
```
