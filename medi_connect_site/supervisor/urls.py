from django.conf.urls import url
from django.contrib.auth import views as auth_views
from supervisor import views as supervisor_views

urlpatterns = [
    url(r'^login/$', auth_views.login, {'template_name': 'supervisor_login.html'}, name='supervisor_login'),
    url(r'^home/(?P<id>\d+)/$',supervisor_views.supervisor, name = 'supervisor_home'),
    url(r'^logout/', auth_views.logout, {'next_page': '/supervisor/login'}, name='logout'),
    url(r'^trans_signup/(?P<id>\d+)/$',supervisor_views.trans_signup ,name = 'trans_signup'),
    url(r'^detail/(?P<id>\d+)/(?P<order_id>\d+)/$',supervisor_views.detail ,name = 'detail'),
    url(r'^assign/(?P<id>\d+)/(?P<order_id>\d+)/$',supervisor_views.assign ,name = 'assign'),
    url(r'^approve/(?P<id>\d+)/(?P<order_id>\d+)/$',supervisor_views.approve ,name = 'approve'),
    url(r'^manage_files/(?P<id>\d+)/(?P<order_id>\d+)/$',supervisor_views.manage_files ,name = 'manage_files'),
    #url(r'^customer_list/(?P<id>\d+)/$',supervisor_views.customer_list,name = 'customer_list'),
    #url(r'^translator_list/(?P<id>\d+)/$',supervisor_views.translator_list,name = 'translator_list'),
]

