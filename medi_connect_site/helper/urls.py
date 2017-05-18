from django.conf.urls import url
from helper import views

urlpatterns = [
    url(r'^hospital/(?P<name>\w+)/$', views.hospital, name="hospital_order"),
    url(r'^order/orderInfo/$', views.order_info, name="order_info"),
]
