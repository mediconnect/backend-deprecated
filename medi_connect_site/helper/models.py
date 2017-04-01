from __future__ import unicode_literals
from django.db import models
from customer.models import Customer
# from translator.models import Translator


# Create your models here.
class Hospital(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField()
    area = models.CharField(max_length=50)
    capacity = models.IntegerField()
    website = models.URLField()
    introduction = models.TextField()

    class Meta:
        db_table = 'hospital'


class Disease(models.Model):
    name = models.CharField(max_length=50)
    category = models.CharField(max_length=50)
    keyword = models.CharField(max_length=150)

    class Meta:
        db_table = 'disease'


class Rank(models.Model):
    rank = models.IntegerField()
    hospital = models.OneToOneField(Hospital)
    disease = models.OneToOneField(Disease)

    class Meta:
        db_table = 'rank'


class Order(models.Model):
    customer = models.OneToOneField(Customer)
    hospital = models.OneToOneField(Hospital)
    disease = models.OneToOneField(Disease)
    # translator = models.OneToOneField(Translator)

    class Meta:
        db_table = 'order'


class Status(models.Model):
    order = models.OneToOneField(Order)
    is_paid = models.BinaryField()
    is_translated = models.BinaryField()
    is_confirmed = models.BinaryField()
    is_delivered = models.BinaryField()
    is_emergency = models.BinaryField()
    is_completed = models.BinaryField()

    class Meta:
        db_table = 'status'
