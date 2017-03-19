from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Customer(models.Model):
    user = models.ForeignKey(User)
    date = models.DateTimeField(auto_now_add=True)
