from django.conf.urls import url
from helper import views

urlpatterns = [
    url(r'^hospital/(?P<name>\w+)/$', views.hospital, name="hospital_order"),
    url(r'^order/orderInfoFirst/$', views.order_info_first, name="order_info_first"),
]
