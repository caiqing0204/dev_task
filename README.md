# dev_task
dev_task是一款基于django-celery-beat调度执行的任务管理平台，平台基于celery4.1.1开发，实现了类似crontab定时执行任务的功能。(后期将作为运维平台dev_system的任务编排组件)<br>
### 当前版本：v0.2
1. 平台已经实现邮件告警，支持通知多人邮件
2. UI界面的微调整
3. 删除了添加任务界面的rabbitmq相关配置
4. 修复了0.1版本中执行任务结果显示的bug
5. 任务结果支持分页，条件搜索等
### 下个版本v1.0
主要添加监控
## 环境：
建议大家在centos7.0系统安装此项目<br>
Python2.7版本以上<br>
项目部署目录 /opt<br>
关闭防火墙<br>
setenforce 0<br>
service iptables stop<br>
安装mysql5.6,rabbitmq,并且启动服务<br>
安装supervisor，必须是3.0以上的版本，centos6.5yum安装默认是2.+的版本，这里需要手动安装。<br>
## 依赖
```
yum install -y epel-release
yum clean all
yum install -y python python-dev python-devel   python-pip  gcc  msgpack-python openssl openssl-devel  mysql-devel
```
## server端和client节点都需要安装的模块，并且git clone代码到server和client上
```
pip install django==1.11.9
pip install django-celery-beat==1.0.1
pip install celery==4.1.1
pip install MySQL-python==1.2.5
pip install SQLAlchemy==1.2.10
pip install msgpack==0.5.6
git clone https://github.com/caiqing0204/dev_task.git
```

## server端安装
关于rabbitmq日志文件等信息的配置，大家可以查官网，自行配置<br>
###### 创建用户，添加user_tags，创建vhost，用户授权
```
rabbitmqctl add_user rabbitmqadmin 1234qwer
rabbitmqctl set_user_tags rabbitmqadmin administrator
rabbitmqctl add_vhost dev_task
rabbitmqctl set_permissions -p dev_task rabbitmqadmin ".*" ".*" ".*"
```

### 安装uwsgi
```
pip install uwsgi==2.0.17.1
```
### 配置dev_task.conf
配置好相应的mysql，rabbitmq信息

### 安装django-celery-result和项目
```
cd /opt/dev_task/
python manage.py makemigrations
python manage.py migrate
cd /opt/dev_task/supply/django-celery-results-master/
python setup.py install
```
### 创建登录用户
```
python /opt/dev_task/createsuperuser.py
```
### 部署supervisord
```
cp /opt/dev_task/server_supervisord.conf /etc/supervisord.conf
supervisord -c /etc/supervisord.conf
```
### 静态文件目录授权
```
chmod 777 /opt/dev_task/static/ -R
```
### 启动nginx,关于nginx配置和修改，可以自己随意定制，不必按照本文档进行,可参考文档部分进行部署配置。
```
cp /opt/dev_task/nginx.conf  /usr/local/nginx/conf/
```
### 登录
http://ip:port<br>
admin<br>
password!23456

## client端安装
### 配置dev_task.conf
配置好相应的mysql，rabbitmq信息

### 安装django-celery-result
```
cd /opt/dev_task/supply/django-celery-results-master/
python setup.py install
```
### 部署supervisord
```
cp /opt/dev_task/client_supervisord.conf /etc/supervisord.conf
supervisord -c /etc/supervisord.conf
```
## 注意
### server端和client端一样
升级完python版本以后，需要重新安装一下pip，下载pip的tar包，解压安装。重新制定软连接，就可以使用了。
我这里是手动安装supervisord 3版本的，安装supervisord之前，需要安装setuptools，centos6.5 yum安装supervisord，版本是2.1,
有问题，欢迎随时提交issues！
