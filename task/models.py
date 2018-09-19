# -*- coding:utf-8 -*-

from __future__ import unicode_literals
from django.db import models
from django_celery_beat.models import PeriodicTask


class TimedTask(PeriodicTask):
    nice_name = models.CharField(max_length=255, default='', blank=True)
    host = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(max_length=50, verbose_name=u"邮箱")
    is_send_email = models.BooleanField(default=True, db_index=True, editable=False)
    run_status = models.BooleanField(default=True, db_index=True, editable=False)
