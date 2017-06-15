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
RECEIVED = 2  # translator finish translating case and submit to hospitals
FEEDBACK = 3  # recieve feedback from hospital
APPROVED = 4  # supervisor aprove translated feedback
FINISHED = 5  # all steps finished

STATUS_CHOICES = (
    (STARTED, 'started'),
    (SUBMITTED, 'submitted'),
    (RECEIVED, 'received'),
    (FEEDBACK, 'feedback'),
    (APPROVED, 'approved'),
    (FINISHED, 'finished')
)

# Translator Sequence
trans_list = Translator.objects.all().values_list('id', flat=True)


def move(translator_id, new_position):
    old_position = trans_list.index(translator_id)
    trans_list.insert(new_position, trans_list.pop(old_position))


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
    overall_rank = models.IntegerField(default=0)
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
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
    translator = models.ForeignKey(Translator, on_delete=models.CASCADE, null=True)
    supervisor = models.ForeignKey(Supervisor, on_delete=models.CASCADE, null=True)
    submit = models.DateField(default=datetime.date.today)
    assign = models.DateTimeField(blank=True, null=True)
    upload = models.DateTimeField(blank=True, null=True)
    description = models.CharField(max_length=255, blank=True)
    required = models.BooleanField(default=False)
    document = models.FileField(upload_to=order_directory_path, null=True)
    extra_document = models.FileField(upload_to=order_directory_path, null=True)
    approved = models.BooleanField(default=False)
    comment = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = 'document'

    @classmethod
    def customer_create(cls, order_id, description, file):
        customer_document = cls(order=order_id, description=description, document=file)
        return customer_document

    def assign(self):
        # find translator
        assign_time = datetime.date.today
        self.assign = assign_time
        translator_id = trans_list[0]
        self.translator = translator_id
        move(translator_id, -1)

        self.assign = assign_time
        self.translator = translator_id

    def sup_approve(self, supervisor_id, comment):
        self.approved = True
        self.supervisor = supervisor_id
        self.comment = comment

    def trans_upload(self, order_id, translator_id, upload_time):
        self.order = order_id
        self.translator = translator_id
        self.upload = upload_time
