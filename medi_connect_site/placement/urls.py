from django.conf.urls import url
from placement import views
from django.views.generic.base import TemplateView

urlpatterns = [
    url(r'^hospital/$', views.hospital_detail, name="hospital_detail"),
    url(r'^hospital/bookmark/$', views.like_hospital, name="like_hospital"),
    url(r'^hospital/comment/$', views.get_comment, name="get_comment"),
    url(r'^order/patients/$', views.order_patient_info, name="order_patient_info"),
    url(r'^order/select/$', views.order_patient_select, name="order_patient_select"),
    url(r'^order/document/$', views.order_document_info, name="order_document_info"),
    url(r'^order/review/$', views.order_review, name="order_review"),
    url(r'^order/deposit/$', views.pay_deposit, name="order_deposit"),
    url(r'^order/submit/$', views.finish, name="order_finish"),
    url(r'^order/order_check/$', views.order_check, name="order_check"),
    url(r'^order/delete_document/$', views.delete_document, name="delete_document"),
]
