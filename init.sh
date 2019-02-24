#!/bin/bash
sed -i "s/rabbitmq_host = 127.0.0.1/rabbitmq_host = $RA_HOST/g" /opt/dev_task/dev_task.conf
sed -i "s/rabbitmq_queue = 127.0.0.1/rabbitmq_queue = $RA_Q/g" /opt/dev_task/dev_task.conf
sed -i "s/rabbitmq_routing_key = 127.0.0.1/rabbitmq_routing_key = $RA_ROUTING_KEY/g" /opt/dev_task/dev_task.conf
sed -i "s/email_host = smtp.exmail.qq.com/email_host = $EM_HOST/g" /opt/dev_task/dev_task.conf
sed -i "s/email_port = 25/email_port = $EM_PORT/g" /opt/dev_task/dev_task.conf
sed -i "s/email_host_user = example@163.com/email_host_user = $EM_SEND_USER/g" /opt/dev_task/dev_task.conf
sed -i "s/email_host_password = 123456/email_host_password = $EM_PASS/g" /opt/dev_task/dev_task.conf
sed -i "s/default_email_user = user1@163.com,user2@163.com/default_email_user = $DEFAULT_EM_ADDR/g" /opt/dev_task/dev_task.conf
sed -i "s/host_ip = 127.0.0.1/host_ip = $LO_HOST/g" /opt/dev_task/dev_task.conf
\cp server_supervisord.conf /etc/supervisord.conf
supervisord -c /etc/supervisord.conf
chmod 777 /opt/dev_task/static/ -R
cp nginx.conf /etc/nginx/
chmod +x /opt/dev_task/init.sh
chmod +x /opt/dev_task/start_server.sh