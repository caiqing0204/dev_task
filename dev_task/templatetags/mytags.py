# coding: utf-8

import re
import ast
import time

from django import template

register = template.Library()
from django_celery_beat.models import IntervalSchedule, CrontabSchedule

'''
@register.filter(name='groups2str')
def groups2str(group_list):
    """
    将用户组列表转换为str
    """

    return ' '.join([group["groupname"] for group in group_list])
    
'''


@register.filter(name='intervals2str')
def intervals2str(interval_id):
    interval_obj = IntervalSchedule.objects.get(id=interval_id)
    return 'every %s %s' % (interval_obj.every, interval_obj.period)


@register.filter(name='crontab2str')
def crontab2str(crontab_id):
    crontab_obj = CrontabSchedule.objects.get(id=crontab_id)
    return '%s %s %s %s %s (m/h/dM/MY/d)' % (crontab_obj.minute, crontab_obj.hour, crontab_obj.day_of_month, crontab_obj.month_of_year, crontab_obj.day_of_week)




