from django.conf.urls import url, include
from task import taskurls, views


urlpatterns = [
    url(r'^$', views.Dashboard.as_view(), name="index"),
    url(r'^task/', include(taskurls)),
    url(r'^login/$', views.LoginView.as_view(), name='login'),
    url(r'^logout/$', views.LogoutView.as_view(), name='logout'),
]

