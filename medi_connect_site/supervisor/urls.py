from django.conf.urls import url
from django.contrib.auth import views as auth_views
import views as supervisor_views
from core import views as core_views

urlpatterns = [
    url(r'^login/$', core_views.auth, name='supervisor_login'),
    url(r'^logout/', auth_views.logout, {'next_page': '/supervisor/login'}, name='supervisor_logout'),



    url(r'^home/(?P<id>\d+)/$',supervisor_views.supervisor, name = 'supervisor_home'),
    url(r'^orders/(?P<id>\d+)/(?P<status>\w+)/$',supervisor_views.order_status, name = 'order_status'),
    url(r'^ajax/update_result/$', supervisor_views.update_result, name='update_result'),
    url(r'^ajax/validate_pwd/$', supervisor_views.validate_pwd, name='validate_pwd'),

    url(r'^trans_signup/(?P<id>\d+)/$',supervisor_views.trans_signup ,name = 'trans_signup'),
    #url(r'^send_password/$', auth_views.password_reset, {'template_name': 'reset_password.html'}, name='send_password'),

    url(r'^detail/(?P<id>\d+)/(?P<order_id>\d+)/$',supervisor_views.detail ,name = 'detail'),
    url(r'^assign/(?P<id>\d+)/(?P<order_id>\d+)/$',supervisor_views.assign ,name = 'assign'),
    url(r'^approve/(?P<id>\d+)/(?P<order_id>\d+)/$',supervisor_views.approve ,name = 'approve'),
    url(r'^generate_questionnaire/(?P<hospital_id>\d+)/(?P<disease_id>\d+)/$',supervisor_views.generate_questionnaire ,name = 'generate_questionnaire'),
    url(r'^manage_files/(?P<id>\d+)/(?P<order_id>\d+)/$',supervisor_views.manage_files ,name = 'manage_files'),
    url(r'^customer_list/(?P<id>\d+)/$',supervisor_views.customer_list,name = 'customer_list'),
    url(r'^translator_list/(?P<id>\d+)/$',supervisor_views.translator_list,name = 'translator_list'),

    url(r'^hospital_list/(?P<id>\d+)/$',supervisor_views.hospital_list,name = 'hospital_list'),
    url(r'^hospital_detail/(?P<id>\w+)/$',supervisor_views.rank_manage,name ='hospital_detail'),
    url(r'^ajax/set_slots/$', supervisor_views.set_slots, name='set_slots'),
]

