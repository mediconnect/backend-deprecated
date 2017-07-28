from django.conf.urls import url
from core import views

urlpatterns = [
    # url address used by front end Ajax call
    url(r'^username_check/$', views.username_check, name='username_check'),
    # url address used by front end Ajax call
    url(r'^email_check/$', views.email_check, name='email_check'),
]
