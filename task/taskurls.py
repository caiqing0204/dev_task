from django.conf.urls import url
from django.views.generic import TemplateView
import views


urlpatterns = [
    url(r'^$', views.Dashboard.as_view(), name="index"),
    url(r'^job/list/$', views.JobList.as_view(), name="job_list"),
    url(r'^job/add/$', views.JobAdd.as_view(), name="job_add"),
    url(r'^job/edit/(?P<id>\d+)/$', views.JobEdit.as_view(), name="job_edit"),
    url(r'^job/del/$', views.JobDel.as_view(), name="job_del"),
    url(r'^job/interval/list/$', views.JobIntervalList.as_view(), name="job_interval_list"),
    url(r'^job/interval/add/$', views.JobIntervalAdd.as_view(), name="job_interval_add"),
    url(r'^job/interval/edit/(?P<id>\d+)/$', views.JobIntervalEdit.as_view(), name="job_interval_edit"),
    url(r'^job/interval/del/$', views.JobIntervalDel.as_view(), name="job_interval_del"),
    url(r'^job/crontab/list/$', views.JobCronatbList.as_view(), name="job_crontab_list"),
    url(r'^job/crontab/add/$', views.JobCrontabAdd.as_view(), name="job_crontab_add"),
    url(r'^job/crontab/edit/(?P<id>\d+)/$', views.JobCrontabEdit.as_view(), name="job_crontab_edit"),
    url(r'^job/crontab/del/$', views.JobCrontabDel.as_view(), name="job_crontab_del"),
    url(r'^job/result/list', views.JobResultList.as_view(), name="job_result_list"),
    url(r'^api/flower/celeryworker', views.CeleryWorker.as_view(), name="api_flower"),
    url(r'^api/rabbitmq', views.Rabbitmq.as_view(), name="api_rabbitmq")
]
