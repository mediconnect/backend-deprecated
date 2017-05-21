from __future__ import unicode_literals
from django.db import models
from customer.models import Customer
from django.db.models import F
import datetime
"""
class ListField(models.TextField):
    __metaclass__ = models.SubfieldBase
    description = "Stores a python list"

    def __init__(self, *args, **kwargs):
        super(ListField, self).__init__(*args, **kwargs)

    def count(self):
        return  

    def to_python(self, value):
        if not value:
            value = []

        if isinstance(value, list):
            return value

        return ast.literal_eval(value)

    def get_prep_value(self, value):
        if value is None:
            return value

        return unicode(value)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value)

class ListModel(models.Model):
    test_list = ListField()

# from translator.models import Translator
# Create choices
"""
# Diseases
DISEASE_CATAGORY_CHOICES = (
    ('CANCER', 'Cancer'),
    ('COLD', 'Cold')
)

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
RECIEVED = 2
FEEDBACK = 3
PAID = 4

STATUS_CHOICES = (
    (STARTED, 'started'),
    (SUBMITTED, 'submitted'),
    (RECIEVED, 'recieved'),
    (FEEDBACK, 'feedback'),
    (PAID, 'paid')
)


# Create your models here.
class Patient(models.Model):

    customer_id = models.ForeignKey(Customer, on_delete = models.CASCADE)
    name = models.CharField(blank = True, max_length=50)
    age = models.IntegerField(blank = True)
    gender = models.CharField(max_length=5,choices=GENDER_CHOICES, default = MALE)
    catagory = models.CharField(max_length = 50,choices = DISEASE_CATAGORY_CHOICES,default = 'COLD')
    diagnose_hospital = models.TextField(blank = True)

    doctor = models.TextField(blank=True)


class Hospital(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField(blank = True)
    area = models.CharField(blank = True, max_length=50)
    slots_open = models.IntegerField(default = 20)
    website = models.URLField(blank = True)
    introduction = models.TextField(default = 'intro')
    specialty = models.TextField(default = 'specialty')
    feedback_time = models.CharField(default = 'one week', max_length=50)
    price_range = models.CharField(default = 'unkown', max_length=50)

    class Meta:
        db_table = 'hospital'
    """
    def get_slots(self):
        return self.slots_open
    """


class Disease(models.Model):
    name = models.CharField(default = 'unknown',max_length=50)
    category = models.CharField(default = 'unkown', max_length=50)
    keyword = models.CharField(default = 'unkown',max_length=150)

    class Meta:
        db_table = 'disease'


class Rank(models.Model):
    rank = models.IntegerField(default = 0)
    hospital = models.OneToOneField(Hospital)
    disease = models.OneToOneField(Disease)

    class Meta:
        db_table = 'rank'


def slots_open_default(hospital):
    H = Hospital.objects.get(pk=hospital)
    return H.slots_open
class Appointment(models.Model):
    hospital = models.ForeignKey('Hospital',on_delete =models.CASCADE)
    """
    week_1 = models.PositiveSmallIntegerField(default = slots_open_default(hospital))
    week_2 = models.PositiveSmallIntegerField(default = slots_open_default(hospital))
    week_3 = models.PositiveSmallIntegerField(default = slots_open_default(hospital))
    week_4 = models.PositiveSmallIntegerField(default = slots_open_default(hospital))
    """
    week_1 = models.PositiveSmallIntegerField(default = 0)
    week_2 = models.PositiveSmallIntegerField(default = 0)
    week_3 = models.PositiveSmallIntegerField(default = 0)
    week_4 = models.PositiveSmallIntegerField(default = 0)
    
class Order(models.Model):
    customer = models.ForeignKey(Customer,on_delete = models.CASCADE)
    patient = models.ForeignKey('Patient', on_delete = models.CASCADE)
    document_id = models.ForeignKey('Document', on_delete= models.CASCADE)
    hospital = models.ForeignKey('Hospital',on_delete= models.CASCADE)
    disease = models.ForeignKey('Disease',on_delete=models.CASCADE)
    #translator = models.ForeignKey('Translator',on_delete = models.CASCADE)
    order_time = models.DateField(default = datetime.date.today)
    estimate_feedback = models.CharField(blank = True,max_length=50)
    status = models.CharField(blank = True,max_length=20,choices=STATUS_CHOICES)

    class Meta:
        db_table = 'order'


def order_directory_path(instance, filename):
    return 'order_{0}/{1}'.format(instance.orer.id, filename)


class Document(models.Model):
    order_id = models.ForeignKey('Order', on_delete=models.CASCADE)
    case_not_trans = models.FileField(blank = True, upload_to = order_directory_path)
    case_trans = models.FileField(blank = True, upload_to = order_directory_path)
    feedback_not_trans = models.FileField(blank = True, upload_to = order_directory_path)
    feedback_trans = models.FileField(blank = True, upload_to = order_directory_path)

