from django.db import models
from django.contrib.auth.models import User
import datetime


# Create your models here.
class Customer(models.Model):
    user = models.OneToOneField(User)
    wechat = models.CharField(blank=True, max_length=50)
    weibo = models.CharField(blank=True, max_length=50)
    qq = models.CharField(blank=True, max_length=50)
    tel = models.CharField(default='unknown', max_length=50)
    address = models.CharField(blank=True, max_length=50)
    zipcode = models.CharField(default='unknown', max_length=50)
    register_time = models.DateField(default=datetime.date.today)

    class Meta:
        db_table = 'auth_customer'

    def get_name(self):
        name = self.user.first_name + ' ' + self.user.last_name
        if name is not ' ':
            return name
        return self.user.username
