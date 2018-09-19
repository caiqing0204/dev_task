from django.conf.urls import url
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
import views


urlpatterns = [
    url(r'^$', views.Dashboard.as_view(), name="index"),
    url(r'^job/list/$', views.job_list.as_view(), name="job_list"),
    url(r'^job/add/$', views.job_add.as_view(), name="job_add"),
    url(r'^job/edit/(?P<id>\d+)/$', views.job_edit.as_view(), name="job_edit"),
    url(r'^job/del/$', views.job_del.as_view(), name="job_del"),
    url(r'^job/interval/list/$', views.job_interval_list.as_view(), name="job_interval_list"),
    url(r'^job/interval/add/$', views.job_interval_add.as_view(), name="job_interval_add"),
    url(r'^job/interval/edit/(?P<id>\d+)/$', views.job_interval_edit.as_view(), name="job_interval_edit"),
    url(r'^job/interval/del/$', views.job_interval_del.as_view(), name="job_interval_del"),
    url(r'^job/crontab/list/$', views.job_cronatb_list.as_view(), name="job_crontab_list"),
    url(r'^job/crontab/add/$', views.job_crontab_add.as_view(), name="job_crontab_add"),
    url(r'^job/crontab/edit/(?P<id>\d+)/$', views.job_crontab_edit.as_view(), name="job_crontab_edit"),
    url(r'^job/crontab/del/$', views.job_crontab_del.as_view(), name="job_crontab_del"),
    url(r'^job/result/list', views.job_result_list.as_view(), name="job_result_list"),
]

