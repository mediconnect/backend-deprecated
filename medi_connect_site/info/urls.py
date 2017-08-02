from info import views
from django.conf.urls import url

# In this url file, id may refer to different models id
urlpatterns = [
    url(r'^profile/$', views.profile, name="info_profile"),
    url(r'^profile/password/$', views.profile_password, name="info_profile_password"),
    url(r'^profile/patient/$', views.profile_patient, name="info_profile_patient"),
    url(r'profile/patient/edit/(?P<patient_id>\d+)/$', views.profile_patient_edit, name="info_profile_patient_edit"),
    url(r'^order/$', views.order, name="info_order"),
    url(r'^order/payment/(?P<order_id>\d+)/$', views.order_pay, name="info_order_pay"),
    url(r'^order/checkout/(?P<order_id>\d+)/$', views.process_order, name="info_order_process"),
    url(r'^order/extradoc/(?P<order_id>\d+)/$', views.add_doc, name="add_doc"),
    url(r'^bookmark/$', views.bookmark, name="info_bookmark"),
    url(r'^unmark/(?P<hospital_id>\d+)/$', views.unmark, name="info_unmark"),
]
