from django.conf.urls import url
from placement import views
from django.views.generic.base import TemplateView

urlpatterns = [
    url(r'^hospital/(?P<hospital_id>\d+)/(?P<disease_id>\d+)/$', views.hospital_detail, name="hospital_order"),
    url(r'^hospital/bookmark/$', views.like_hospital, name="like_hospital"),
    url(r'^hospital/comment/$', views.get_comment, name="get_comment"),
    url(r'^order/basic/(?P<disease_id>\d+)/(?P<hospital_id>\d+)/(?P<slot_num>\d+)$', views.fast_order, name="fast_order"),
    url(r'^order/basic/(?P<order_id>\d+)/(?P<slot_num>\d+)/$', views.order_info_first, name="order_info_first"),
    url(r'^order/basic/(?P<order_id>\d+)/$', views.order_info_first, name="order_info_first"),
    url(r'^order/disease/(?P<order_id>\d+)/$', views.order_submit_first, name="order_submit_first"),
    url(r'^order/patients/(?P<order_id>\d+)/$', views.order_patient_select, name="order_patient_select"),
    url(r'^order/patients/(?P<order_id>\d+)/(?P<patient_id>\d+)/$', views.order_patient_finish,
        name="order_patient_finish"),
    url(r'^order/document/(?P<order_id>\d+)/$', views.order_submit_second, name="order_submit_second"),
    url(r'^order/deposit/(?P<order_id>\d+)/$', views.pay_deposit, name="order_deposit"),
    url(r'^order/deposit/(?P<order_id>\d+)/(?P<amount>\d+)/$', views.pay_deposit, name="order_deposit"),
    url(r'^order/submit/(?P<order_id>\d+)/$', views.finish, name="order_finish"),
    url(r'^order/order_check/$', views.order_check, name="order_check"),
    url(r'^order/order_expire/$', TemplateView.as_view(template_name='order_expire.html'), name="order_expire")
]
