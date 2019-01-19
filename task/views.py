# -*- coding:utf-8 -*-

from django_celery_beat.models import IntervalSchedule, CrontabSchedule, PeriodicTask
from dev_task.celery import (rabbitmq_exchange, rabbitmq_routing_key, rabbitmq_queue,
                             rabbitmq_host, rabbitmq_password, rabbitmq_user,rabbitmq_vhost)
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models.signals import pre_save, pre_delete
from django_celery_results.models import TaskResult
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import AccessMixin
from django.contrib import auth
from django.shortcuts import HttpResponseRedirect, HttpResponse
from django.shortcuts import render as my_render
from django.urls import reverse, reverse_lazy
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.generic import TemplateView, ListView, CreateView, UpdateView
from django.views.generic.edit import FormView
from django.views.generic.base import View
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from dev_task.settings import default_email_users
from datetime import datetime
from celery import current_app
from models import TimedTask
from forms import LoginForm
from supply.rabbitmq_api import MQManage
import json
import urllib, urllib2, base64


class LoginRequiredMixin(AccessMixin):

    @method_decorator(login_required(redirect_field_name='next', login_url='/login/'))
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)


@method_decorator(sensitive_post_parameters(), name='dispatch')
@method_decorator(csrf_protect, name='dispatch')
@method_decorator(never_cache, name='dispatch')
class LoginView(FormView):
    template_name = 'login.html'
    form_class = LoginForm
    redirect_field_name = 'next'

    def get_context_data(self, **kwargs):
        kwargs = super(LoginView, self).get_context_data(**kwargs)
        kwargs.update({
            'next': self.request.GET.get('next', '')
        })
        return kwargs

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return HttpResponseRedirect(reverse('index'))
        else:
            return super(LoginView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        login_form = self.get_form()
        if login_form.is_valid():
            user_name = login_form.cleaned_data['username']
            pass_word = login_form.cleaned_data['password']
            next = request.POST.get('next', '')
            user = authenticate(username=user_name, password=pass_word)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    if next:
                        return HttpResponseRedirect(next)
                    else:
                        return HttpResponseRedirect(reverse('index'))
                else:
                    return my_render(request, "login.html", {"msq": _(u"用户未激活，请联系管理！")})
            else:
                return my_render(request, "login.html", {"msq": _(u"用户验证失败，请联系管理员！")})
        else:
            return my_render(request, "login.html", {"msq": _(u"用户验证失败，请联系管理员！"), "login_form": login_form})


class LogoutView(View):
    def get(self, request):
        auth.logout(request)
        return HttpResponseRedirect("/login/")


# dashboard
class Dashboard(LoginRequiredMixin, View):
    def get(self, request):
        return my_render(request, "index.html", locals())


# api celery worker
class CeleryWorker(LoginRequiredMixin, View):
    def get(self, request):
        requests = urllib2.Request('http://%s:5555/dashboard?json=1' % rabbitmq_host)
        response = urllib2.urlopen(requests).read()
        return HttpResponse(response)


# api rabbitmq
class Rabbitmq(LoginRequiredMixin, View):
    def get(self, request):
        mq = MQManage()
        mq.create_connection(rabbitmq_host, rabbitmq_user, rabbitmq_password)
        queuelist = json.dumps({"data": [x for x in json.loads(mq.list_queues()) if not x["name"].startswith('celery')]})
        return HttpResponse(queuelist)


# job list
class JobList(LoginRequiredMixin, ListView):
    model = TimedTask
    template_name = "task/job_list.html"
    context_object_name = "jobs_info"


# job add
class JobAdd(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = TimedTask
    fields = '__all__'
    template_name = "task/job_add.html"
    celery_app = current_app
    celery_app.loader.import_default_modules()
    interval_info = IntervalSchedule.objects.all()
    crontab_info = CrontabSchedule.objects.all()

    def get_context_data(self, **kwargs):
        context = {
            "interval_info": IntervalSchedule.objects.all(),
            "crontab_info": CrontabSchedule.objects.all(),
            "tasks": list(sorted(name for name in self.celery_app.tasks if not name.startswith('celery.'))),
            "default_email_user": default_email_users
        }
        kwargs.update(context)
        return super(JobAdd, self).get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        post_data = request.POST
        enabled_value = str(post_data.get("enabled")) == str(True)
        is_send_email_value = str(post_data.get("is_send_email")) == str(True)

        job_data = {
            "nice_name": post_data.get("nice_name", ''),
            "host": post_data.get("host", ''),
            "name": post_data.get("name", ''),
            "task": post_data.get("regtask", ''),
            "interval_id": post_data.get("interval", ''),
            "crontab_id": post_data.get("crontab", ''),
            "args": post_data.get("args", ''),
            "kwargs": post_data.get("kwargs", ''),
            "queue": str(rabbitmq_queue),
            "exchange": rabbitmq_exchange,
            "routing_key": str(rabbitmq_routing_key),
            "expires": None,
            "enabled": enabled_value,
            "run_status": True if enabled_value else False,
            "description": post_data.get("description", ''),
            "email": post_data.get("email"),
            "is_send_email": is_send_email_value
        }
        print job_data
        if job_data['interval_id'] and job_data['crontab_id']:
            error = u"you can only choices one of interval or crontab!"
            interval_info = self.interval_info
            crontab_info = self.crontab_info
            self.celery_app.loader.import_default_modules()
            tasks = list(sorted(name for name in self.celery_app.tasks if not name.startswith('celery.')))
            return my_render(request, "task/job_add.html", locals())
        value = job_data["kwargs"]
        try:
            json.loads(value)
        except ValueError as exc:
            error = u"Unable to parse JSON: %s" % exc
            interval_info = self.interval_info
            crontab_info = self.crontab_info
            self.celery_app.loader.import_default_modules()
            tasks = list(sorted(name for name in self.celery_app.tasks if not name.startswith('celery.')))
            return my_render(request, "task/job_add.html", locals())
        if job_data['args']:
            try:
                json.loads(job_data['args'])
            except Exception as exc:
                error = u"Unable to parse JSON: %s" % exc
                interval_info = self.interval_info
                crontab_info = self.crontab_info
                self.celery_app.loader.import_default_modules()
                tasks = list(sorted(name for name in self.celery_app.tasks if not name.startswith('celery.')))
        try:
            pre_save.send(sender=PeriodicTask, instance=TimedTask)
            TimedTask.objects.create(**job_data)
            msg = u"添加任务成功!"
        except Exception as e:
            error = u"添加任务失败!,{0}".format(e)
        interval_info = self.interval_info
        crontab_info = self.crontab_info
        self.celery_app.loader.import_default_modules()
        tasks = list(sorted(name for name in self.celery_app.tasks if not name.startswith('celery.')))
        return my_render(request, "task/job_add.html", locals())


# job edit
class JobEdit(LoginRequiredMixin, UpdateView):
    model = TimedTask
    pk_url_kwarg = 'id'
    context_object_name = 'job_info'
    template_name = 'task/job_edit.html'
    fields = '__all__'
    celery_app = current_app
    celery_app.loader.import_default_modules()
    interval_info = IntervalSchedule.objects.all()
    crontab_info = CrontabSchedule.objects.all()

    def get_context_data(self, **kwargs):
        kwargs = super(JobEdit, self).get_context_data(**kwargs)
        kwargs.update({
            "interval_info": self.interval_info,
            "crontab_info": self.crontab_info,
            "tasks": list(sorted(name for name in self.celery_app.tasks if not name.startswith('celery.'))),
            "status": 0
        })
        return kwargs

    def get_queryset(self):
        qs = super(JobEdit, self).get_queryset()
        return qs.filter(pk=self.kwargs.get(self.pk_url_kwarg))

    def post(self, request, *args, **kwargs):
        post_data = request.POST
        enabled_value = str(post_data.get("enabled")) == str(True)
        is_send_email_value = str(post_data.get("is_send_email")) == str(True)
        job_data = {
            "nice_name": post_data.get("nice_name", ''),
            "host": post_data.get("host", ''),
            "name": post_data.get("name", ''),
            "interval_id": post_data.get("interval", ''),
            "crontab_id": post_data.get("crontab", ''),
            "args": post_data.get("args", ''),
            "kwargs": post_data.get("kwargs", ''),
            "queue": post_data.get("queue", ''),
            "enabled": enabled_value,
            "run_status": True if enabled_value else False,
            "exchange": post_data.get("exchange", ''),
            "routing_key": post_data.get("routing_key", ''),
            "expires": None,
            "description": post_data.get("description", ''),
            "date_changed": datetime.now(),
            "email": post_data.get("email"),
            "is_send_email": is_send_email_value
        }
        if job_data['interval_id'] and job_data['crontab_id']:
            status = 2
            return my_render(request, "task/job_edit.html", locals())
        task_value = post_data.get("regtask")
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
            self.get_queryset().update(**job_data)
            status = 1
        except Exception as e:
            print e
            status = 2
        return my_render(request, "task/job_edit.html", locals())


# job del
class JobDel(LoginRequiredMixin, View):

    def post(self, request):
        pre_delete.send(sender=PeriodicTask, instance=TimedTask)
        jobs = request.POST.getlist("job_check", [])
        if jobs:
            for v in jobs:
                TimedTask.objects.filter(pk=v).delete()
        return HttpResponseRedirect(reverse('job_list'))


# job interval list
class JobIntervalList(LoginRequiredMixin, ListView):
    model = IntervalSchedule
    context_object_name = 'interval_info'
    template_name = "task/interval_list.html"


# job interval add
class JobIntervalAdd(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = IntervalSchedule
    template_name = 'task/interval_add.html'
    fields = '__all__'
    success_url = reverse_lazy('job_interval_add')
    success_message = _("<b>interval</b> was created successfully")


# job interval del
class JobIntervalDel(LoginRequiredMixin, View):

    def post(self, request):
        pre_delete.send(sender=PeriodicTask, instance=TimedTask)
        intervals = request.POST.getlist("interval_check", [])
        if intervals:
            for v in intervals:
                IntervalSchedule.objects.filter(pk=v).delete()
        return HttpResponseRedirect(reverse('job_interval_list'))


# job interval edit
class JobIntervalEdit(LoginRequiredMixin, UpdateView):
    model = IntervalSchedule
    fields = '__all__'
    template_name = 'task/interval_edit.html'
    pk_url_kwarg = 'id'
    context_object_name = 'interval_info'

    def get_context_data(self, **kwargs):
        kwargs = super(JobIntervalEdit, self).get_context_data(**kwargs)
        kwargs.update({
            "status": 0
        })
        return kwargs

    def get_queryset(self):
        qs = super(JobIntervalEdit, self).get_queryset()
        return qs.filter(pk=self.kwargs.get(self.pk_url_kwarg))

    def post(self, request, *args, **kwargs):
        post_data = request.POST
        interval_data = {
            "every": post_data.get("every"),
            "period": post_data.get("period")
        }
        try:
            pre_save.send(sender=PeriodicTask, instance=TimedTask)
            self.get_queryset().update(**interval_data)
            status = 1
        except:
            status = 2
        return my_render(request, "task/interval_edit.html", locals())


# job crontab list
class JobCronatbList(LoginRequiredMixin, ListView):
    model = CrontabSchedule
    template_name = 'task/crontab_list.html'
    context_object_name = 'crontab_info'


# job crontab add
class JobCrontabAdd(LoginRequiredMixin, View):
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
class JobCrontabDel(LoginRequiredMixin, View):
    def post(self, request):
        pre_delete.send(sender=PeriodicTask, instance=TimedTask)
        crontabs = request.POST.getlist("crontab_check", [])
        if crontabs:
            for v in crontabs:
                CrontabSchedule.objects.filter(pk=v).delete()
        return HttpResponseRedirect(reverse('job_crontab_list'))


# job crontab edit
class JobCrontabEdit(LoginRequiredMixin, View):
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
class JobResultList(LoginRequiredMixin, View):

    def get(self, request):
        result_dict = {}
        left = []
        right = []
        first = False
        last = False
        left_has_more = False
        right_has_more = False
        is_paginated = True

        host_ip = request.GET.get('host', '')
        status = request.GET.get('status', '')
        kwargs = request.GET.get('kwargs', '')
        page = request.GET.get('page', 1)
        timedtask_obj = TimedTask.objects.all()
        result_list = TaskResult.objects.all()

        if host_ip and kwargs:
            result_dict['task_kwargs__contains'] = host_ip and kwargs
        elif host_ip:
            result_dict['task_kwargs__contains'] = host_ip
        elif kwargs:
            result_dict['task_kwargs__contains'] = kwargs
        if status:
            result_dict['status__contains'] = status
        if result_dict:
            result_list = TaskResult.objects.filter(**result_dict)
        total_result = result_list.count()
        page_number = int(page)
        paginator = Paginator(result_list, 10)
        # 获得分页后的总页数
        total_pages = paginator.num_pages
        page_range = list(paginator.page_range)
        currentPage = int(page_number)


        try:
            result_list = paginator.page(page)
        except PageNotAnInteger:
            result_list = paginator.page(1)
        except EmptyPage:
            result_list = paginator.page(total_pages)

        if result_list:
            if page_number == 1:
                right = page_range[page_number:page_number + 2]
                if right[-1] < total_pages - 1:
                    right_has_more = True

                if right[-1] < total_pages:
                    last = True

            elif page_number == total_pages:
                left = page_range[(page_number - 3) if (page_number - 3) > 0 else 0:page_number - 1]
                if left[0] > 2:
                    left_has_more = True
                if left[0] > 1:
                    first = True
            else:
                left = page_range[(page_number - 3) if (page_number - 3) > 0 else 0:page_number - 1]
                right = page_range[page_number:page_number + 2]
                if right[-1] < total_pages - 1:
                    right_has_more = True
                if right[-1] < total_pages:
                    last = True
                if left[0] > 2:
                    left_has_more = True
                if left[0] > 1:
                    first = True
        else:
            is_paginated = False

        return my_render(request, "task/result_list.html", locals())
