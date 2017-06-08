from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.auth import authenticate, login

urlpatterns = [
    url(r'^login/$', auth_views.login, {'template_name': 'login.html'},name='translator/login'),
    url(r'^logout/', auth_views.logout, {'next_page': '/'}, name='logout'),
    url(r'^admin/', admin.site.urls),
]