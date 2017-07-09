from __future__ import unicode_literals
from django.db import models
from customer.models import Customer
from django.contrib.auth.models import User
from translator.models import Translator_C2E, Translator_E2C
import datetime
import random

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
SUBMITTED = 1  # deposit paid, only change appointment at this status
TRANSLATING_ORIGIN = 2  # translator starts translating origin documents
RECEIVED = 3  # origin documents translated, approved and submitted to hospitals
# ============ Above is C2E status =============#
# ============Below is E2C status ==============#
RETURN = 4  # hospital returns feedback
TRANSLATING_FEEDBACK = 5  # translator starts translating feedback documents
FEEDBACK = 6  # feedback documents translated, approved, and feedback to customer
PAID = 7  # remaining amount paid

STATUS_CHOICES = (
    (STARTED, 'started'),
    (SUBMITTED, 'submitted'),
    (TRANSLATING_ORIGIN, 'translating_origin'),
    (RECEIVED, 'received'),
    (RETURN, 'return'),
    (TRANSLATING_FEEDBACK, 'translating_feedback'),
    (FEEDBACK, 'feedback'),
    (PAID, 'PAID'),
)

# Trans_status

NOT_STARTED = 0  # assignment not started yet
ONGOING = 1  # assignment started not submitted to supervisor
APPROVING = 2  # assignment submitted to supervisor for approval
APPROVED = 3  # assignment approved, to status 5
DISAPPROVED = 4  # assignment disapproved, return to status 1
FINISHED = 5  # assignment approved and finished

TRANS_STATUS_CHOICE = (
    (NOT_STARTED, 'not_started'),
    (ONGOING, 'ongoing'),
    (APPROVING, 'approving'),
    (APPROVED, 'approved'),
    (DISAPPROVED, 'disapproved'),
    (FINISHED, 'finished'),
)

trans_list_C2E = list(Translator_C2E.objects.filter(is_staff = True).values_list('id',flat=True))
trans_list_E2C = list(Translator_E2C.objects.filter(is_staff = True).values_list('id',flat=True))


# Function to move the position of a translator in sequence
def move(trans_list, translator_id, new_position):
    old_position = trans_list.index(translator_id)
    trans_list.insert(new_position, trans_list.pop(old_position))
    return trans_list


class Patient(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    name = models.CharField(blank=True, max_length=50)
    age = models.IntegerField(blank=True)
    gender = models.CharField(max_length=5, choices=GENDER_CHOICES, default=MALE)
    category = models.CharField(max_length=50, default='COLD')
    diagnose_hospital = models.CharField(max_length=50, blank=True)
    doctor = models.TextField(blank=True)

    class Meta:
        db_table = 'patient'


class Hospital(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField(blank=True)
    area = models.CharField(blank=True, max_length=50)
    default_slots = models.IntegerField(default = 20)
    slots_open_0 = models.IntegerField(default=20)
    slots_open_1 = models.IntegerField(default = 20)
    slots_open_2 = models.IntegerField(default=20)
    slots_open_3 = models.IntegerField(default=20)
    overall_rank = models.IntegerField(default=0)
    website = models.URLField(blank=True)
    introduction = models.TextField(default='intro')
    specialty = models.TextField(default='specialty')
    feedback_time = models.CharField(default='one week', max_length=50)
    price_range = models.CharField(default='unknown', max_length=50)

    class Meta:
        db_table = 'hospital'

    def reset_slot(self):
        self.slots_open_0 = self.slots_open_1
        self.slots_open_1 = self.slots_open_2
        self.slots_open_2 = self.slots_open_3
        self.slots_open_3 = self.default_slots
        self.save()
        print self.slots_open_0

    def set_default_slots(self,slot):
        self.default_slots = slot
        self.slots_open_0 = self.default_slots
        self.slots_open_1 = self.default_slots
        self.slots_open_2 = self.default_slots
        self.slots_open_3 = self.default_slots


class Disease(models.Model):
    name = models.CharField(default='unknown', max_length=50)
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
    # translator Chinese to English
    translator_C2E = models.ForeignKey(Translator_C2E, on_delete=models.CASCADE, null=True,
                                       related_name='chinese_translator')
    # translator English to Chinese
    translator_E2C = models.ForeignKey(Translator_E2C, on_delete=models.CASCADE, null=True,
                                       related_name='english_translator')
    # supervisor = models.ForeignKey(Supervisor, on_delete = models.CASCADE, null = True)
    # only one supervisor for now, no need to keep this info
    hospital = models.ForeignKey('Hospital', on_delete=models.CASCADE, null=True)
    disease = models.ForeignKey('Disease', on_delete=models.CASCADE, null=True)
    week_number_at_submit = models.IntegerField(default = 0)
    #use week_number_at_submit to hold the week number and calculate the submit deadline
    submit = models.DateField(default=datetime.date.today) #datetime of receiving the order
    # all origin document uploaded by customer
    origin = models.ManyToManyField('Document', related_name='original_file')
    # all feedback document TRANSLATED and APPROVED
    feedback = models.ManyToManyField('Document', related_name='feedback_file')
    # all pending document, make sure this NOT VISIBLE to customers
    pending = models.ManyToManyField('Document', related_name='pending_file')
    receive = models.DateField(default=datetime.date.today)
    status = models.CharField(blank=True, max_length=20, choices=STATUS_CHOICES)
    trans_status = models.CharField(blank=True, max_length=20, choices=TRANS_STATUS_CHOICE)

    class Meta:
        db_table = 'order'

    def get_info(self):
        return 'Order id is ' + str(self.id) + ' Deadline is :' + self.get_deadline()

    def get_week(self):
        return self.weeknumber_at_submit - (datetime.today.isocalendar()[1]-self.submit.isocalendar()[1])

    def get_deadline(self):  # default deadline 2 days after submit
        return str(self.submit + datetime.timedelta(days=2))  # date time algebra

    def get_submit_deadline(self):
        d = "%s-W%s"%(self.submit.isocalendar()[0],self.submit.isocalendar()[1])
        return datetime.datetime.strptime(d + '-0', "%Y-W%W-%w")

    def get_status(self):
        return self.status

    def get_trans_status(self):
        return self.trans_status

    def change_status(self, status):
        self.status = status

    def change_trans_status(self,status):
        self.trans_status = status

def order_directory_path(instance, filename):
    return 'order_{0}/{1}/{2}'.format(instance.order.customer.get_name(), instance.order.id, filename)


class Document(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
    description = models.CharField(max_length=50, blank=True)
    required = models.BooleanField(default=False)
    is_origin = models.BooleanField(default=True)
    is_translated = models.BooleanField(default=False)
    upload_at = models.DateTimeField(auto_now_add=True)
    comment = models.CharField(max_length=255, blank=True)
    document = models.FileField(upload_to=order_directory_path, null=True)

    class Meta:
        db_table = 'document'