from info import views
from django.conf.urls import url

urlpatterns = [
    url(r'^profile/(?P<id>\d+)/$', views.profile, name="info_profile"),
    url(r'^profile/password/(?P<id>\d+)/$', views.profile_password, name="info_profile_password"),
    url(r'^profile/patient/(?P<id>\d+)/$', views.profile_patient, name="info_profile_patient"),
    url(r'^order/(?P<id>\d+)/$', views.order, name="info_order"),
    url(r'^order/payment/(?P<id>\d+)/$', views.order_pay, name="info_order_pay"),
    url(r'^order/checkout/(?P<id>\d+)/$', views.process_order, name="info_order_process"),
    url(r'^order/extradoc/(?P<id>\d+)/$', views.add_doc, name="add_doc"),
]
