from info import views
from django.conf.urls import url

urlpatterns = [
    url(r'^profile/(?P<id>\d+)/$', views.profile, name="info_profile"),
url(r'^profile/password/(?P<id>\d+)/$', views.profile_password, name="info_profile_password"),
    url(r'^order/(?P<id>\d+)/$', views.order, name="info_order"),
]