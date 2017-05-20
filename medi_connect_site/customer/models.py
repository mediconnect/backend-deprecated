from django.db import models
from django.contrib.auth.models import User


# Create your models here.

# Create your models here.
class Customer(models.Model):
    user = models.OneToOneField(User)
    email = models.EmailField()
    wechat = models.TextField(blank=True)
    weibo = models.TextField(blank=True)
    qq = models.TextField(blank=True)
    tel = models.TextField()
    address = models.TextFiled()
    zipcode = models.IntegerField()
    register_time = models.DateField(auto_now_add=True)
    favorite_hospitals = models.OneToManyField(Hospital)

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
