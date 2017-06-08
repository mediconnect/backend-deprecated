from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.auth import authenticate, login
import views as trans_views

urlpatterns = [
	url(r'^home/',trans_views.translator,name = 'translator_home' ),
    url(r'^login/$', auth_views.login, {'template_name': 'login.html'},name='translator/login'),
    url(r'^logout/', auth_views.logout, {'next_page': '/'}, name='logout'),
    url(r'^upload/',trans_views.upload,name = 'upload')
]