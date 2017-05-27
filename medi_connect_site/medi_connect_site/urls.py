from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from core import views as core_views
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', core_views.home, name='home'),
    url(r'^login/', auth_views.login, {'template_name': 'core/login.html'},
        name='login'),
    url(r'^logout/', auth_views.logout, {'next_page': '/'}, name='logout'),
    url(r'^signup/', core_views.signup, name='signup'),
    url(r'^search/', core_views.search, name='search'),
    url(r'^result/', core_views.result, name='result'),
    url(r'^customer/', include('customer.urls')),
    url(r'^helper/', include('helper.urls')),
    url(r'^info/', include('info.urls')),
]

urlpatterns += staticfiles_urlpatterns()
