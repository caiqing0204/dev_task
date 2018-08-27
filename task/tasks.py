#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals
from celery import shared_task
from subprocess import Popen, PIPE
import os
import sys
import ConfigParser
from dev_task import settings
import django

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dev_task.settings')
django.setup()

config = ConfigParser.ConfigParser()
config.read(os.path.join(settings.BASE_DIR, 'dev_task.conf'))
host_ip = config.get("localhost", 'host_ip')


@shared_task
def exec_command_or_script(host, cmd):
    if str(host) == str(host_ip):
        try:
            p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
            data = p.communicate()
            return data
        except Exception as e:
            return e
    else:
        return "localhost:%s The choice of your target machine is a problem!" % host_ip
