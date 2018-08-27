# -*- coding:utf-8 -*-

import json
from datetime import date, datetime
from django.shortcuts import HttpResponse, HttpResponseRedirect
from django.views.generic.base import View
from django.core.urlresolvers import reverse
from django.contrib import auth
from django.contrib.auth import authenticate, login
from django.shortcuts import render as my_render
from django.contrib.auth.decorators import login_required
from django_celery_beat.models import IntervalSchedule, CrontabSchedule, PeriodicTask
from django_celery_results.models import TaskResult
from models import TimedTask
from celery import current_app
# from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import pre_save, pre_delete
from forms import LoginForm


class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view, login_url='/login/')


class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated():
            return HttpResponseRedirect(reverse('index'))
        else:
            return my_render(request, "login.html", {})

    def post(self, request):
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user_name = login_form.cleaned_data['username']
            pass_word = login_form.cleaned_data['password']
            user = authenticate(username=user_name, password=pass_word)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect(reverse('index'))
                else:
                    return my_render(request, "login.html", {"msq": u"用户未激活，请联系管理！"})
            else:
                return my_render(request, "login.html", {"msq": u"用户验证失败，请联系管理员！"})
        else:
            return my_render(request, "login.html", {"msq": u"用户验证失败，请联系管理员！", "login_form": login_form})


class LogoutView(View):
    def get(self, request):
        auth.logout(request)
        return HttpResponseRedirect("/login/")


# 仪表盘
class Dashboard(LoginRequiredMixin, View):
    def get(self, request):
        # host_num = AssetInfo.objects.count()
        # hostgroup_num = AssetGroup.objects.count()
        # remoteuser_num = RemoteUser.objects.count()
        # user_num = UserProfile.objects.count()
        return my_render(request, "index.html")


# job list
class job_list(LoginRequiredMixin, View):
    def get(self, request):
        jobs_info = TimedTask.objects.all()
        return my_render(request, "task/job_list.html", locals())


# job add
class job_add(LoginRequiredMixin, View):
    celery_app = current_app

    def get(self, request):
        interval_info = IntervalSchedule.objects.all()
        crontab_info = CrontabSchedule.objects.all()
        _ = self.celery_app.loader.import_default_modules()
        tasks = list(sorted(name for name in self.celery_app.tasks if not name.startswith('celery.')))
        return my_render(request, "task/job_add.html", locals())

    def post(self, request):
        enabled_value = str(request.POST.get("enabled")) == str(True)
        job_data = {
            "nice_name": request.POST.get("nice_name", ''),
            "host": request.POST.get("host", ''),
            "name": request.POST.get("name", ''),
            "task": request.POST.get("regtask", ''),
            "interval_id": request.POST.get("interval", ''),
            "crontab_id": request.POST.get("crontab", ''),
            "args": request.POST.get("args", ''),
            "kwargs": request.POST.get("kwargs", ''),
            "queue": request.POST.get("queue", ''),
            "exchange": request.POST.get("exchange", ''),
            "routing_key": request.POST.get("routing_key", ''),
            "expires": request.POST.get("expires") if request.POST.get("expires") else None,
            "enabled": enabled_value,
            "description": request.POST.get("description", '')
        }
        if job_data['interval_id'] and job_data['crontab_id']:
            error = u"you can only choices one of interval or crontab!"
            interval_info = IntervalSchedule.objects.all()
            crontab_info = CrontabSchedule.objects.all()
            _ = self.celery_app.loader.import_default_modules()
            tasks = list(sorted(name for name in self.celery_app.tasks if not name.startswith('celery.')))
            return my_render(request, "task/job_add.html", locals())
        value = job_data["kwargs"]
        try:
            json.loads(value)
        except ValueError as exc:
            error = u"Unable to parse JSON: %s" % exc
            interval_info = IntervalSchedule.objects.all()
            crontab_info = CrontabSchedule.objects.all()
            _ = self.celery_app.loader.import_default_modules()
            tasks = list(sorted(name for name in self.celery_app.tasks if not name.startswith('celery.')))
            return my_render(request, "task/job_add.html", locals())
        if job_data['args']:
            try:
                json.loads(job_data['args'])
            except Exception as exc:
                error = u"Unable to parse JSON: %s" % exc
                interval_info = IntervalSchedule.objects.all()
                crontab_info = CrontabSchedule.objects.all()
                _ = self.celery_app.loader.import_default_modules()
                tasks = list(sorted(name for name in self.celery_app.tasks if not name.startswith('celery.')))
        try:
            pre_save.send(sender=PeriodicTask, instance=TimedTask)
            TimedTask.objects.create(**job_data)
            msg = u"添加任务成功!"
        except Exception as e:
            error = u"添加任务失败!,{0}".format(e)
        interval_info = IntervalSchedule.objects.all()
        crontab_info = CrontabSchedule.objects.all()
        _ = self.celery_app.loader.import_default_modules()
        tasks = list(sorted(name for name in self.celery_app.tasks if not name.startswith('celery.')))
        return my_render(request, "task/job_add.html", locals())


# job edit
class job_edit(LoginRequiredMixin, View):
    celery_app = current_app

    def get(self, request, id):
        status = 0
        job_info = TimedTask.objects.get(pk=id)
        interval_info = IntervalSchedule.objects.all()
        crontab_info = CrontabSchedule.objects.all()
        _ = self.celery_app.loader.import_default_modules()
        tasks = list(sorted(name for name in self.celery_app.tasks if not name.startswith('celery.')))
        return my_render(request, "task/job_edit.html", locals())

    def post(self, request, id):
        enabled_value = str(request.POST.get("enabled")) == str(True)
        job_data = {
            "nice_name": request.POST.get("nice_name", ''),
            "host": request.POST.get("host", ''),
            "name": request.POST.get("name", ''),
            "interval_id": request.POST.get("interval", ''),
            "crontab_id": request.POST.get("crontab", ''),
            "args": request.POST.get("args", ''),
            "kwargs": request.POST.get("kwargs", ''),
            "queue": request.POST.get("queue", ''),
            "enabled": enabled_value,
            "exchange": request.POST.get("exchange", ''),
            "routing_key": request.POST.get("routing_key", ''),
            "expires": request.POST.get("expires") if request.POST.get("expires") else None,
            "description": request.POST.get("description", ''),
            "date_changed": datetime.now()
        }
        if job_data['interval_id'] and job_data['crontab_id']:
            status = 2
            return my_render(request, "task/job_edit.html", locals())
        task_value = request.POST.get("regtask")
        if task_value:
            job_data["task"] = task_value
        kwargs_vaule = job_data["kwargs"]
        args_value = job_data["args"]
        try:
            json.loads(kwargs_vaule)
        except:
            status = 2
            return my_render(request, "task/job_edit.html", locals())
        if args_value:
            try:
                json.loads(args_value)
            except:
                status = 2
                return my_render(request, "task/job_edit.html", locals())
        try:
            pre_save.send(sender=PeriodicTask, instance=TimedTask)
            TimedTask.objects.filter(id=id).update(**job_data)
            status = 1
        except Exception as e:
            print e
            status = 2
        return my_render(request, "task/job_edit.html", locals())


# job del
class job_del(LoginRequiredMixin, View):

    def post(self, request):
        pre_delete.send(sender=PeriodicTask, instance=TimedTask)
        jobs = request.POST.getlist("job_check", [])
        if jobs:
            for v in jobs:
                TimedTask.objects.filter(pk=v).delete()
        return HttpResponseRedirect(reverse('job_list'))


# job interval list
class job_interval_list(LoginRequiredMixin, View):
    def get(self, request):
        interval_info = IntervalSchedule.objects.all()
        return my_render(request, "task/interval_list.html", locals())


# job interval add
class job_interval_add(LoginRequiredMixin, View):
    def get(self, request):
        return my_render(request, "task/interval_add.html")

    def post(self, request):
        interval_data = {
            "every": request.POST.get("every", ''),
            "period": str(request.POST.get("period", ''))
        }
        try:
            IntervalSchedule.objects.create(**interval_data)
            msg = u"添加interval成功!"

        except:
            error = u"添加interval失败!"
        return my_render(request, "task/interval_add.html", locals())


# job interval del
class job_interval_del(LoginRequiredMixin, View):
    def post(self, request):
        pre_delete.send(sender=PeriodicTask, instance=TimedTask)
        intervals = request.POST.getlist("interval_check", [])
        if intervals:
            for v in intervals:
                IntervalSchedule.objects.filter(pk=v).delete()
        return HttpResponseRedirect(reverse('job_interval_list'))


# job interval edit
class job_interval_edit(LoginRequiredMixin, View):
    def get(self, request, id):
        status = 0
        interval_info = IntervalSchedule.objects.get(pk=id)
        return my_render(request, "task/interval_edit.html", locals())

    def post(self, request, id):
        interval_data = {
            "every": request.POST.get("every"),
            "period": request.POST.get("period")
        }
        try:
            pre_save.send(sender=PeriodicTask, instance=TimedTask)
            IntervalSchedule.objects.filter(pk=id).update(**interval_data)
            status = 1
        except:
            status = 2
        return my_render(request, "task/interval_edit.html", locals())


# job crontab list
class job_cronatb_list(LoginRequiredMixin, View):
    def get(self, request):
        crontab_info = CrontabSchedule.objects.all()
        return my_render(request, "task/crontab_list.html", locals())


# job crontab add
class job_crontab_add(LoginRequiredMixin, View):
    def get(self, request):
        return my_render(request, "task/crontab_add.html", locals())

    def post(self, request):
        crontab_data = {
            "minute": request.POST.get("minute", ''),
            "hour": request.POST.get("hour", ''),
            "day_of_week": request.POST.get("day_of_week", ''),
            "day_of_month": request.POST.get("day_of_month", ''),
            "month_of_year": request.POST.get("month_of_year", '')
        }
        try:
            CrontabSchedule.objects.create(**crontab_data)
            msg = u"添加crontab成功!"
        except:
            error = u"添加crontab失败!"
        return my_render(request, "task/crontab_add.html", locals())


# job crontab del
class job_crontab_del(LoginRequiredMixin, View):
    def post(self, request):
        pre_delete.send(sender=PeriodicTask, instance=TimedTask)
        crontabs = request.POST.getlist("crontab_check", [])
        if crontabs:
            for v in crontabs:
                CrontabSchedule.objects.filter(pk=v).delete()
        return HttpResponseRedirect(reverse('job_crontab_list'))


# job crontab edit
class job_crontab_edit(LoginRequiredMixin, View):
    def get(self, request, id):
        status = 0
        crontab_info = CrontabSchedule.objects.get(pk=id)
        return my_render(request, "task/crontab_edit.html", locals())

    def post(self, request, id):
        crontab_data = {
            "minute": request.POST.get("minute", ''),
            "hour": request.POST.get("hour", ''),
            "day_of_week": request.POST.get("day_of_week", ''),
            "day_of_month": request.POST.get("day_of_month", ''),
            "month_of_year": request.POST.get("month_of_year", '')
        }
        try:
            pre_save.send(sender=PeriodicTask, instance=TimedTask)
            CrontabSchedule.objects.filter(pk=id).update(**crontab_data)
            status = 1
        except:
            status = 2
        return my_render(request, "task/crontab_edit.html", locals())


# job result list
class job_result_list(LoginRequiredMixin, View):
    def get(self, request):
        result_info = TaskResult.objects.all()
        return my_render(request, "task/result_list.html", locals())
