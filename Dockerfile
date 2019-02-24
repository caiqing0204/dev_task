FROM centos7-nginx
MAINTAINER jeaner
USER root

RUN yum install -y epel-release
RUN yum -y update
RUN yum install -y python python-dev python-devel   python-pip  gcc  msgpack-python openssl openssl-devel  mysql-devel git wget supervisor mysql
WORKDIR /opt
RUN git clone https://github.com/caiqing0204/dev_task.git
WORKDIR dev_task/
RUN pip install --upgrade pip
RUN pip install -r requirements
RUN pip install uwsgi==2.0.17.1
WORKDIR /opt/dev_task/supply/django-celery-results-master/
RUN python setup.py install
EXPOSE 8070
WORKDIR /opt/dev_task
RUN chmod +x /opt/dev_task/init.sh
RUN chmod +x /opt/dev_task/start_server.sh
ENTRYPOINT ["/bin/bash","-c","/opt/dev_task/init.sh && /opt/dev_task/start_server.sh start"]
