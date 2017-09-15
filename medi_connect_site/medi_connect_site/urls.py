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
    url(r'^login/', core_views.auth, name='auth'),
    url(r'^logout/', auth_views.logout, {'next_page': '/'}, name='logout'),
    url(r'^signup/', core_views.signup, name='signup'),
    url(r'^result/', core_views.result, name='result'),
    url(r'^result_guest/', core_views.result_guest, name='result_guest'),
    url(r'^hospital/', core_views.hospital, name='hospital_list'),
    url(r'^disease/', core_views.disease, name='disease_list'),
    url(r'^contact/$', core_views.contact, name='contact'),
    url(r'^core/', include('core.urls')),
    url(r'^translator/', include('translator.urls')),
    url(r'^supervisor/', include('supervisor.urls')),
    url(r'^customer/', include('customer.urls')),
    url(r'^helper/', include('helper.urls')),
    url(r'^info/', include('info.urls')),
    # javascript plugin reverse look up url
    url(r'^jsreverse/$', js_views.urls_js, name='js_reverse'),
]

urlpatterns += staticfiles_urlpatterns()
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
