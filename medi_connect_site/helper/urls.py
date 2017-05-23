from django.conf.urls import url
from helper import views

urlpatterns = [
    url(r'^hospital/(?P<name>\w+)/$', views.hospital, name="hospital_order"),
    url(r'^order/orderInfoFirst/(?P<order_id>\d+)/$', views.order_info_first, name="order_info_first"),
    url(r'^order/orderSubmitFirst/(?P<order_id>\d+)/$', views.order_submit_first, name="order_submit_first"),
    url(r'^order/orderSubmitSecond/(?P<order_id>\d+)/$', views.order_submit_second, name="order_submit_second"),
]
