#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals
import os
from django.conf import settings
from celery import Celery, platforms
import ConfigParser
from kombu import Queue, Exchange
# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dev_task.settings')
app = Celery('dev_task')

# redis connect code
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config = ConfigParser.ConfigParser()
config.read(os.path.join(BASE_DIR, 'dev_task.conf'))
rabbitmq_host = config.get('rabbitmq', 'rabbitmq_host')
rabbitmq_port = config.get('rabbitmq', 'rabbitmq_port')
rabbitmq_user = config.get('rabbitmq', 'rabbitmq_user')
rabbitmq_password = config.get('rabbitmq', 'rabbitmq_password')
rabbitmq_vhost = config.get('rabbitmq', 'rabbitmq_vhost')
rabbitmq_exchange = config.get('rabbitmq', 'rabbitmq_exchange')
rabbitmq_queue = config.get('rabbitmq', 'rabbitmq_queue')
rabbitmq_routing_key = config.get('rabbitmq', 'rabbitmq_routing_key')

app.conf.broker_url = 'amqp://{0}:{1}@{2}:{3}/{4}'.format(rabbitmq_user, rabbitmq_password, rabbitmq_host, rabbitmq_port, rabbitmq_vhost)
media_exchange = Exchange('{0}'.format(rabbitmq_exchange), type='topic')
queue = (
    Queue('{0}'.format(rabbitmq_queue), media_exchange, routing_key='{0}'.format(rabbitmq_routing_key)),
)
route = {
    'work.notify.email.send_mail': {
        'queue': '{0}'.format(rabbitmq_queue),
        'routing_key': '{0}'.format(rabbitmq_routing_key)
    }
}
app.conf.update(CELERY_QUEUES=queue, CELERY_ROUTES=route)
# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')


# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
# lambda: settings.INSTALLED_APPS


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))

