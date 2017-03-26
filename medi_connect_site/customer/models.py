from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Customer(models.Model):
    user = models.OneToOneField(User)
    date = models.DateField(auto_now=True)
    telephone = models.TextField(default='unknown')
    address = models.TextField(default='unknown')
    zipcode = models.TextField(default='unknown')

    class Meta:
        db_table = 'auth_customer'

    def get_name(self):
        name = self.user.first_name + ' ' + self.user.last_name
        if name is not ' ':
            return name
        return self.user.username

    def set_attributes(self, tel, address, zipcode):
        print len(tel)
        self.telephone = tel if len(tel) < 1 else 'unknown'
        self.address = address if len(address) < 1 else 'unknown'
        self.zipcode = zipcode if len(zipcode) < 1 else 'unknown'
