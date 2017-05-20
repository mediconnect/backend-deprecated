from __future__ import unicode_literals
from django.db import models
#from customer.models import Customer

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

#Diseases
DISEASE_CATAGORY_CHOICES = (
    (CANCER,'Cancer'),
    (COLD,'Cold')
    )

#Gender
MALE = 'M'
FEMALE = 'F'

GENDER_CHOICES = (
    (MALE,'Male'),
    (FEMALE,'Female'),
    (OTHER, 'Other')
    )

#Status
STARTED = 0
SUBMITTED = 1 #only change appointment at this status
RECIEVED = 2
FEEDBACK = 3
PAID = 4

STATUS_CHOICES = (
    (STARTED, 'started'),
    (SUBMITTED,'submitted'),
    (RECIEVED,'recieved'),
    (FEEDBACK,'feedback'),
    (PAID,'paid')
    )


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
    favorite_hospitals = models.ListField()
class Patient(models.Model):
    customer_id = models.ForeignKey('Customer', on_delete = models.CASCADE)
    name = models.CharField(max_length=50)
    age = models.IntegerField()
    gender = models.CharField(max_length=5,choices=GENDER_CHOICES)
    catagory = models.CharField(max_length = 50,choices = DISEASE_CATAGORY_CHOICES,default = COLD)
    diagnose_hospital = models.TextField()
    doctor = models.TextField(blank=True)

class Hospital(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField()
    area = models.CharField(max_length=50)
    slots_open = models.IntegerField()
    website = models.URLField()
    introduction = models.TextField()
    specialty = models.TextField()
    feedback_time = models.CharField(max_length=50)
    price_range = models.CharField(max_length=50)
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

class Appointment(models.Model):
    hospital = models.ForeignKey('Hospital',on_delete =CASCADE)
    week_1 = models.PositiveSmallIntegerField()
    week_2 = models.PositiveSmallIntegerField()
    week_3 = models.PositiveSmallIntegerField()
    week_4 = models.PositiveSmallIntegerField()

class Order(models.Model):
    customer = models.ForeignKey('Customer',on_delete = CASCADE)
    patient = models.ForeignKey('Patient', on_delete = CASACADE)
    document = models.ForeignKey('Document', on_delete= CASCADE)
    hospital = models.ForeignKey('Hospital',on_delete= CASCADE)
    disease = models.ForeignKey('Disease',on_delete=CASCADE)
    translator = models.ForeignKey('Translator',on_delete = CASCADE)
    order_time = models.DateField(auto_now_add = True)
    estimate_feedback = models.CharField(max_length=50)
    status = models.CharField(max_length=20,choices=STATUS_CHOICES)

    class Meta:
        db_table = 'order'

def order_directory_path(instance,filename):
    return 'order_{0}/{1}'.format(instance.orer.id,filename)
class Document(models.Model):
    order = models.ForeignKey('Order', on_delete=CASCADE)
    case_not_trans = models.FileFiled(upload_to = order_directory_path)
    case_trans = models.FileFiled(upload_to = order_directory_path)
    feedback_not_trans = models.FileFiled(upload_to = order_directory_path)
    feedback_trans = models.FileFiled(upload_to = order_directory_path)
