from django.conf.urls import url
from core import views

urlpatterns = [
    url(r'^username_check/$', views.username_check, name='username_check'),
    url(r'^email_check/$', views.email_check, name='email_check'),
]
