# from django.conf.urls import url
# from django.contrib import admin
# from django.contrib.auth import views as auth_views
# from django.contrib.auth import authenticate, login
#
#
#
# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#
# urlpatterns = [
#     url(r'^translator/login/$', auth_views.login, {'template_name': 'login.html'},name='translator/login'),
#     url(r'^supervisor/login/$', auth_views.login, {'template_name': 'login.html'},name='supervisor/login'),
#     url(r'^logout/$', auth_views.logout, name='translator/logout'),
#     url(r'^admin/', admin.site.urls),
#     url(r'^$', views.home, name='home'),
# ]