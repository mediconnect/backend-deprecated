from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Customer(models.Model):
    user = models.OneToOneField(User)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'auth_customer'

    def get_name(self):
        if self.user.get_full_name():
            return self.user.get_full_name()
        return self.user.username
