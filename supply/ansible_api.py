#!/usr/bin/python
# -*- coding:utf-8 -*-
import ansible.runner
import sys
from ansible.inventory import Inventory

import os
import django
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dev_task.settings')
django.setup()
from dev_task import settings
dict = {}


class Myrun(object):
    def __init__(self, host_ip, remote_port=58022, module_name='', module_args=''):

        self.host_ip = host_ip
        self.remote_port = remote_port
        self.module_name = module_name
        self.module_args = module_args

    def ansible_run(self):
        ip = Inventory(self.host_ip)
        results = ansible.runner.Runner(
            remote_user='dev_task',
            become='yes',
            become_user='root',
            remote_port=self.remote_port,
            forks=2,
            module_name=self.module_name,
            module_args=self.module_args,
            inventory=ip,
            # pattern='all',
            # host_list="%s,"%(host_ip_port),
            private_key_file='%s/dev_task' % settings.RSA_PRIVATE_KEY_DIR
        ).run()
        try:
            if results is None:
                sys.exit(0)
        except Exception as e:
            return Exception, e

        for (hostname, result) in results['contacted'].items():
            if 'failed' in result:
                return "%s >>> %s" % (hostname, result['msg'])
            else:
                return result

    def exec_cmd(self, cmd):
        self.module_args = '%s' % cmd
        self.module_name = 'shell'
        results = self.ansible_run()
        try:
            return results['stdout']
        except:
            return results

    def exec_scipt(self, cmd):
        self.module_args = '%s' % cmd
        self.module_name = 'script'
        results = self.ansible_run()
        try:
            return results['stdout']
        except:
            return results


