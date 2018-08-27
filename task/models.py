from __future__ import unicode_literals

from django.db import models

from django_celery_beat.models import PeriodicTask


class TimedTask(PeriodicTask):
    nice_name = models.CharField(max_length=255, default='', blank=True)
    host = models.CharField(max_length=255, blank=True, null=True)
