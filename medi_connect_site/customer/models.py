from django.db import models
from django.contrib.auth.models import User
import datetime


# Create your models here.
class Customer(models.Model):
    user = models.OneToOneField(User)
    email = models.EmailField(default='unknown')
    wechat = models.TextField(blank=True)
    weibo = models.TextField(blank=True)
    qq = models.TextField(blank=True)
    tel = models.TextField(default='unknown')
    address = models.TextField(blank=True)
    zipcode = models.TextField(default=0)
    register_time = models.DateField(default=datetime.date.today)

    class Meta:
        db_table = 'auth_customer'

    def get_name(self):
        name = self.user.first_name + ' ' + self.user.last_name
        if name is not ' ':
            return name
        return self.user.username

    def set_attributes(self, tel, address, zipcode):
        self.tel = tel if len(tel) < 1 else 'unknown'
        self.address = address if len(address) < 1 else 'unknown'
        self.zipcode = zipcode if len(zipcode) < 1 else 'unknown'
