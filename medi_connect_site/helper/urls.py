from django.conf.urls import url
from helper import views

urlpatterns = [
    url(r'^(?P<name>\w+)/$', views.hospital, name="hospital_order"),
]
