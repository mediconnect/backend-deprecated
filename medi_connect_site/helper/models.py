from __future__ import unicode_literals
from django.db import models
from customer.models import Customer
from translator.models import Translator
from supervisor.models import Supervisor
import datetime


# Gender
MALE = 'M'
FEMALE = 'F'

GENDER_CHOICES = (
    (MALE, 'Male'),
    (FEMALE, 'Female'),
    ('OTHER', 'Other')
)

# Status
STARTED = 0
SUBMITTED = 1  # only change appointment at this status
RECEIVED = 2   # translator finish translating case and submit to hospitals
FEEDBACK = 3    # recieve feedback from hospital 
APPROVED = 4    # supervisor aprove translated feedback
FINISHED = 5    # all steps finished

STATUS_CHOICES = (
    (STARTED, 'started'),
    (SUBMITTED, 'submitted'),
    (RECEIVED, 'received'),
    (FEEDBACK, 'feedback'),
    (APPROVED,'approved'),
    (FINISHED, 'finished')
)


# Create your models here.
class Patient(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    name = models.CharField(blank=True, max_length=50)
    age = models.IntegerField(blank=True)
    gender = models.CharField(max_length=5, choices=GENDER_CHOICES, default=MALE)
    category = models.CharField(max_length=50, default='COLD')
    diagnose_hospital = models.TextField(blank=True)
    doctor = models.TextField(blank=True)

    class Meta:
        db_table = 'patient'


class Hospital(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField(blank=True)
    area = models.CharField(blank=True, max_length=50)
    slots_open = models.IntegerField(default=20)
    overall_rank = models.IntegerField(default = 0)
    website = models.URLField(blank=True)
    introduction = models.TextField(default='intro')
    specialty = models.TextField(default='specialty')
    feedback_time = models.CharField(default='one week', max_length=50)
    price_range = models.CharField(default='unknown', max_length=50)

    class Meta:
        db_table = 'hospital'


class Disease(models.Model):
    name = models.CharField(default='unknown', max_length=50)
    category = models.CharField(default='unknown', max_length=50)
    keyword = models.CharField(default='unknown', max_length=150)

    class Meta:
        db_table = 'disease'


class Rank(models.Model):
    rank = models.IntegerField(default=0)
    hospital = models.OneToOneField(Hospital)
    disease = models.OneToOneField(Disease)

    class Meta:
        db_table = 'rank'


def slots_open_default(hospital):
    H = Hospital.objects.get(pk=hospital)
    return H.slots_open


class Appointment(models.Model):
    hospital = models.ForeignKey('Hospital', on_delete=models.CASCADE)
    week_1 = models.PositiveSmallIntegerField(default=0)
    week_2 = models.PositiveSmallIntegerField(default=0)
    week_3 = models.PositiveSmallIntegerField(default=0)
    week_4 = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = 'appointment'


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True)
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE, null=True)
    hospital = models.ForeignKey('Hospital', on_delete=models.CASCADE, null=True)
    disease = models.ForeignKey('Disease', on_delete=models.CASCADE, null=True)
    order_time = models.DateField(default=datetime.date.today)
    estimate_feedback = models.CharField(blank=True, max_length=50)
    status = models.CharField(blank=True, max_length=20, choices=STATUS_CHOICES)

    class Meta:
        db_table = 'order'


def order_directory_path(instance, filename):
    return 'order_{0}/{1}/{2}'.format(instance.order.customer, instance.order.id, filename)


class Document(models.Model):

    order = models.ForeignKey(Order,on_delete = models.CASCADE,null= True)
    translator = models.ForeignKey(Translator,on_delete = models.CASCADE, null = True)
    supervisor = models.ForeignKey(Supervisor, on_delete = models.CASCADE, null = True)
    assign_time = models.DateTimeField(default=datetime.date.today)
    description = models.CharField(max_length = 255, blank = True)
    required = models.BooleanField(default= False)
    document = models.FileField(upload_to = order_directory_path, null = True)
    document_trans = models.FileField(upload_to = order_directory_path, null = True)
    approved = models.BooleanField(default = False)

    class Meta:
        db_table = 'document'

    def approve(self):
        self.approved = True