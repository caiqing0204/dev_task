#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import absolute_import, unicode_literals
from supply.email_send import send_monitor_email
from task.models import TimedTask
from celery import shared_task
from dev_task import settings
import subprocess


@shared_task
def exec_command_or_script(task_name, host, cmd):
    timetask_obj = TimedTask.objects.get(name=task_name)

    if str(host) == str(settings.host_ip):

        try:
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            data = p.communicate()
            if str(p.wait()) != '0':
                if timetask_obj.run_status:
                    timetask_obj.run_status = False
                    timetask_obj.save()
                if timetask_obj.is_send_email:
                    send_monitor_email(str(timetask_obj.email).split(','), str(host), str(cmd).split()[-1], str(cmd), task_name, str(p.wait()))
            elif str(p.wait()) == '0' and not timetask_obj.run_status:
                timetask_obj.run_status = True
                timetask_obj.save()
            if data[0]:
                return ' '.join(data[0].split('\n'))
            else:
                return u"scripts normal running."
        except Exception as e:
            if timetask_obj.run_status:
                timetask_obj.run_status = False
                timetask_obj.save()
            send_monitor_email(str(timetask_obj.email).split(','), str(host), str(cmd).split()[-1], str(cmd), task_name, e)
            return e

    else:
        if timetask_obj.run_status:
            timetask_obj.run_status = False
            timetask_obj.save()
        send_monitor_email(str(timetask_obj.email).split(','), str(host), str(cmd).split()[-1], str(cmd), task_name, u"config error!")
        return "localhost:%s The choice of your target machine is a problem!" % settings.host_ip
