from django.conf.urls import url, include
from task import taskurls, views
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

urlpatterns = [
    url(r'^task/', include(taskurls)),
    url(r'^login/$', views.LoginView.as_view(), name="login"),
    url(r'^logout/$', views.LogoutView.as_view(), name="logout"),
    url(r'^$', login_required(TemplateView.as_view(template_name="index.html")))
]

