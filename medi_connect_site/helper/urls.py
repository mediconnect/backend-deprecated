from django.conf.urls import url
from helper import views

urlpatterns = [
    url(r'^hospital/(?P<hospital_id>\d+)/(?P<disease_id>\d+)/$', views.hospital, name="hospital_order"),
    url(r'^order/basic/(?P<order_id>\d+)/(?P<slot_num>\d+)$', views.order_info_first, name="order_info_first"),
    url(r'^order/disease/(?P<order_id>\d+)/$', views.order_submit_first, name="order_submit_first"),
    url(r'^order/document/(?P<order_id>\d+)/$', views.order_submit_second, name="order_submit_second"),
    url(r'^order/review/(?P<order_id>\d+)/$', views.document_submit, name="document_submit"),
    url(r'^order/submit/(?P<order_id>\d+)/$', views.finish, name="order_finish"),
]
