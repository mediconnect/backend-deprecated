from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Customer(models.Model):
    user = models.OneToOneField(User)

    class Meta:
        db_table = 'auth_customer'

    def get_name(self):
        name = self.user.first_name + ' ' + self.user.last_name
        if name is not None:
            return name
        return self.user.username
