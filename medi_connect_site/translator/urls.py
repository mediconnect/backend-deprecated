from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.auth import authenticate, login
import views as trans_views

urlpatterns = [
    url(r'^home/(?P<id>\d+)/', trans_views.translator, name='trans_home'),
    url(r'^assignment/(?P<id>\d+)/(?P<assignments>)/$', trans_views.assignment_summary, name='assignment_summary'),
    url(r'^login/$', auth_views.login, {'template_name': 'trans_login.html'}, name='translator/login'),
    url(r'^logout/', auth_views.logout, {'next_page': '/'}, name='logout'),
]
