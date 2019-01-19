# -*- coding:utf-8 -*-

from django.core.mail import send_mail
from datetime import datetime
from dev_task.settings import DEFAULT_FROM_EMAIL


def send_monitor_email(email, host, scripts_name, detail, taskname, abnormal):

    email_title = u"dev_task任务管理平台告警"
    email_body = u"""
    告警内容如下:
        脚本主机:{0}
        任务名称:{4}
        脚本名称:{1}
        详情:{2}
        当前时间:{5}
        异常:exit status {3}
    """.format(host, scripts_name, detail, abnormal, taskname, datetime.now())
    send_mail(email_title, email_body, DEFAULT_FROM_EMAIL, email)

