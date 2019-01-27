# coding: utf-8

import json
from django import template
from django_celery_beat.models import IntervalSchedule, CrontabSchedule

register = template.Library()
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
    return '%s %s %s %s %s (m/h/dM/MY/d)' % (
    crontab_obj.minute, crontab_obj.hour, crontab_obj.day_of_month, crontab_obj.month_of_year, crontab_obj.day_of_week)


@register.filter(name='host2str')
def host2str(obj):
    _list = obj.values_list("host", flat=True)
    return list(set(list(_list)))


@register.filter(name='kwargs2str')
def kwargs2str(obj):
    list_1 = []
    _list = obj.values_list("kwargs", flat=True)
    for v in list(list(_list)):
        if isinstance(v, unicode):
            _v = json.loads(v)
            list_1.append(_v['cmd'])
        else:
            list_1.append(v['cmd'])
    return list(set(list_1))


@register.filter(name='cmd2str')
def cmd2str(obj):
    try:
        return json.loads(obj)['cmd']
    except ValueError:
        return eval(obj)[u'cmd']

