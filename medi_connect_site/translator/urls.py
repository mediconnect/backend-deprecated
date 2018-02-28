from django.conf.urls import url
from core import views as core_views
from django.contrib.auth import views as auth_views
import views as trans_views
import info.utility as util

urlpatterns = [
    url(r'^home/(?P<id>\d+)/', trans_views.translator, name='trans_home'),
    url(r'^status/(?P<id>\d+)/(?P<status>\w+)/$', trans_views.translator_status, name='trans_home_status'),
    url(r'^assignment/(?P<id>\d+)/(?P<order_id>\d+)/$', trans_views.assignment_summary, name='assignment_summary'),
    url(r'^login/$', core_views.auth, name='translator_login'),
    url(r'^logout/', auth_views.logout, {'next_page': '/translator/login'}, name='translator_logout'),
    url(r'^ajax/update_result/$', trans_views.update_result, name='trans_update_result'),
    url(r'^force_download/(?P<file_path>(.)+)/$', util.force_download, name='force_download'),

    url(r'^ajax/create_questionnaire/$', trans_views.create_questionnaire, name='create_questionnaire'),
    url(r'^generate_questionnaire/(?P<id>\d+)/(?P<questionnaire_id>\d+)/$', trans_views.generate_questionnaire,
        name='generate_questionnaire'),
]
