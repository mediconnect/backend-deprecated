from django.conf.urls import url
from customer import views

urlpatterns = [
    url(r'^$', views.customer, name='customer'),
]
