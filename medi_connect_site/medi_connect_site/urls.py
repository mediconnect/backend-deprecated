from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from core import views as core_views
from django.contrib.auth import views as auth_views
from django_js_reverse import views as js_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', core_views.home, name='home'),
    url(r'^login/', auth_views.login, {'template_name': 'login.html'},
        name='login'),
    url(r'^logout/', auth_views.logout, {'next_page': '/'}, name='logout'),
    url(r'^signup/', core_views.signup, name='signup'),
    url(r'^result/', core_views.result, name='result'),
    url(r'^result_guest/', core_views.result_guest, name='result_guest'),
    url(r'^hospital/', core_views.hospital, name='hospital_list'),
    url(r'^disease/', core_views.disease, name='disease_list'),
    url(r'^translator/', include('translator.urls')),
    url(r'^supervisor/', include('supervisor.urls')),
    url(r'^customer/', include('customer.urls')),
    url(r'^helper/', include('helper.urls')),
    url(r'^info/', include('info.urls')),
    # javascript plugin reverse look up url
    url(r'^jsreverse/$', js_views.urls_js, name='js_reverse'),
    # password reset url routers
    url(r'^password_reset/$', auth_views.password_reset,
        {'template_name': 'password_reset_form.html'},
        name='password_reset'),
    url(r'^password_reset/done/$', auth_views.password_reset_done, {'template_name': 'password_reset_done.html'},
        name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.password_reset_confirm, {'template_name': 'password_reset_confirm.html'},
        name='password_reset_confirm'),
    url(r'^reset/done/$', auth_views.password_reset_complete, {'template_name': 'password_reset_complete.html'},
        name='password_reset_complete'),
]

urlpatterns += staticfiles_urlpatterns()
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
