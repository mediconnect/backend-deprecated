from django.conf.urls import url
from core import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # url address used by front end Ajax call
    url(r'^username_check/$', views.username_check, name='username_check'),
    # url address used by front end Ajax call
    url(r'^email_check/$', views.email_check, name='email_check'),
    url(r'^disease_choice/$', views.choose_hospital, name='choose_hospital'),
    # password reset url routers
    url(r'^password_reset/$', auth_views.password_reset,
        {'template_name': 'password_reset_form.html'},
        name='password_reset'),
    url(r'^password_reset/done/$', auth_views.password_reset_done, {'template_name': 'password_reset_done.html'},
        name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.password_reset_confirm, {'template_name': 'password_reset_confirm.html'},
        name='password_reset_confirm'),
    url(r'^reset/done/$', auth_views.password_reset_complete, {'template_name': 'password_reset_complete.html'},
        name='password_reset_complete'),
    url(r'^send_response/$', views.send_response, name='send_response'),
    url(r'^hospital/detail/(?P<hospital_id>\d+)/$', views.hospital_detail, name='hospital_detail'),

    # urls to handle questionnaire
    url(r'^questionnaire/(?P<questionnaire_id>\d+)/(?P<access>[a-zA-Z0-9:$&+,:;=?_@#|<>.-^*()%!]+)/$',views.questionnaire,name = 'questionnaire'),
    url(r'^ajax/render_questionnaire/$', views.render_questionnaire, name='render_questionnaire'),
    url(r'^ajax/submit_answer/$', views.submit_answer, name='submit_answer'),

    # urls to handle resubmit documents
    url(r'^resubmit/(?P<order_id>\d+)/$',views.resubmit,name = 'resubmit'),
]
