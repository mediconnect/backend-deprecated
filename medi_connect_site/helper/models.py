# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q
import datetime
from customer.models import Customer
from info import utility as util
from django.utils import timezone

# Function to move the position of a translator in sequence
def auto_assign(order):
    print 'this is called'
    if order.get_status() <= util.TRANSLATING_ORIGIN:
        assignee = Staff.objects.filter(role=1).order_by('sequence')[0]
        order.set_translator_C2E(assignee)
        assignee.set_sequence(timezone.now())
        print assignee.id

    if order.get_status() >= util.RETURN and order.get_status <= util.FEEDBACK:
        assignee = Staff.objects.filter(role=2).order_by('sequence')[0]
        order.set_translator_E2C(assignee)
        assignee.set_sequence(timezone.now())
        print assignee


def manual_assign(order, assignee):
    if order.get_status() <= util.TRANSLATING_ORIGIN:
        order.set_translator_C2E(assignee)
        order.save()
        assignee.set_sequence(timezone.now())

    if order.get_status() >= util.RETURN and order.get_status <= util.FEEDBACK:
        order.set_translator_E2C(assignee)
        order.save()
        assignee.set_sequence(timezone.now())

class Disease(models.Model):
    name = models.CharField(default='unknown', max_length=50)
    keyword = models.CharField(default='unknown', max_length=150)

    class Meta:
        db_table = 'disease'

    def get_name(self):
        return self.name

class Hospital(models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to=util.hospital_directory_path, null=True)
    email = models.EmailField(blank=True)
    area = models.CharField(blank=True, max_length=50)
    default_slots = models.IntegerField(default=20)
    slots_open_0 = models.IntegerField(default=20)
    slots_open_1 = models.IntegerField(default=20)
    slots_open_2 = models.IntegerField(default=20)
    slots_open_3 = models.IntegerField(default=20)
    overall_rank = models.IntegerField(default=0)
    website = models.URLField(blank=True)
    introduction = models.TextField(default='intro')
    specialty = models.TextField(default='specialty')
    feedback_time = models.CharField(default='one week', max_length=50)
    price_range = models.CharField(default='unknown', max_length=50)
    average_score = models.FloatField(null=True)
    review_number = models.IntegerField(blank = True)

    class Meta:
        db_table = 'hospital'

    def get_id(self):
        return self.get_id()

    def get_name(self):
        return self.name

    def reset_slot(self):
        self.slots_open_0 = self.slots_open_1
        self.slots_open_1 = self.slots_open_2
        self.slots_open_2 = self.slots_open_3
        self.slots_open_3 = self.default_slots
        self.save()

    def add_slot(self, week):
        if week == 'all':
            self.slots_open_0 += 1
            self.slots_open_1 += 1
            self.slots_open_2 += 1
            self.slots_open_3 += 1
        if week == 0:
            self.slots_open_0 += 1
        if week == 1:
            self.slots_open_1 += 1
        if week == 2:
            self.slots_open_2 += 1
        if week == 3:
            self.slots_open_3 += 1
        self.save()

    def subtract_slot(self, week):
        if week == 'all':
            self.slots_open_0 -= 1
            self.slots_open_1 -= 1
            self.slots_open_2 -= 1
            self.slots_open_3 -= 1
        if week == 0:
            self.slots_open_0 -= 1
        if week == 1:
            self.slots_open_1 -= 1
        if week == 2:
            self.slots_open_2 -= 1
        if week == 3:
            self.slots_open_3 -= 1
        self.save()

    def set_default_slots(self, slot):
        self.default_slots = slot
        self.slots_open_0 = self.default_slots
        self.slots_open_1 = self.default_slots
        self.slots_open_2 = self.default_slots
        self.slots_open_3 = self.default_slots

    def update_score(self, score):
        if self.review_number == 0:
            assert self.average_score is None, 'average score is not consistent with review number, something went wrong.'
            self.average_score = score
            self.review_number = 1
        else:
            self.average_score = (self.average_score * self.review_number + score) / (self.review_number + 1)
            self.review_number += 1


class Rank(models.Model):
    rank = models.IntegerField(default=0)
    hospital = models.ForeignKey(Hospital, unique=False, default=None, related_name='hospital_rank')
    disease = models.ForeignKey(Disease, unique=False, default=None, related_name='disease_rank')

    class Meta:
        db_table = 'rank'


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True)
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE, null=True)
    patient_order = models.ForeignKey('OrderPatient', on_delete=models.CASCADE, null=True)
    translator_C2E = models.ForeignKey('Staff', on_delete=models.CASCADE, null=True,
                                       related_name='chinese_translator')
    translator_E2C = models.ForeignKey('Staff', on_delete=models.CASCADE, null=True,
                                       related_name='english_translator')
    hospital = models.ForeignKey('Hospital', on_delete=models.CASCADE, null=True)
    disease = models.ForeignKey('Disease', on_delete=models.CASCADE, null=True)
    week_number_at_submit = models.IntegerField(default=0)
    # use week_number_at_submit to hold the week number and calculate the submit deadline
    submit = models.DateTimeField(auto_now_add=True)  # datetime of receiving the order
    # all origin document uploaded by customer
    origin = models.ManyToManyField('Document', related_name='original_file')
    # all feedback document TRANSLATED and APPROVED
    feedback = models.ManyToManyField('Document', related_name='feedback_file')
    # all pending document, make sure this NOT VISIBLE to customers
    latest_upload = models.DateTimeField(null=True)
    pending = models.ManyToManyField('Document', related_name='pending_file')
    receive = models.DateField(default=datetime.date.today)
    status = models.CharField(blank=True, max_length=20, choices=util.STATUS_CHOICES)
    trans_status = models.CharField(default=0, max_length=20, choices=util.TRANS_STATUS_CHOICE)
    auto_assigned = models.BooleanField(default=False)
    deposit_paid = models.BooleanField(default = False) #allow translation after this
    full_payment_paid = models.BooleanField(default = False)


    class Meta:
        db_table = 'order'

    def get_info(self):
        return 'Order id is ' + str(self.id) + ' Deadline is :' + self.get_deadline()

    def get_translator_C2E(self):
        if self.translator_C2E is None:
            return (-1, '未分配')
        else:
            return (self.translator_C2E.id, self.translator_C2E.get_name())

    def set_translator_C2E(self,assignee):
        self.translator_C2E = assignee
        self.save()

    def get_translator_E2C(self):
        if self.translator_E2C is None:
            return (-1, '未分配')
        else:
            return (self.translator_E2C.id, self.translator_E2C.get_name())

    def set_translator_E2C(self, assignee):
        self.translator_E2C = assignee
        self.save()

    def get_patient(self):
        if self.patient_order is None or self.patient is None:
            return (-1, '病人信息缺失')
        else:
            return (self.patient_order.id, self.patient_order.get_name())

    def get_submit(self):
        return self.submit + datetime.timedelta(hours=8)

    def get_remaining(self):  # deadline
        return self.get_submit() + datetime.timedelta(days=2);

    def get_deadline(self):  # default deadline 2 days after submit time remaining
        total_sec = (self.get_submit() + datetime.timedelta(days=2) - datetime.datetime.now(util.utc_8)).total_seconds()
        days = int(total_sec / (3600 * 24))
        hours = int((total_sec - 3600 * 24 * days) / 3600)
        deadline = str(days) + '  天,  ' + str(hours) + '  小时'
        if hours < 0:
            deadline += ('  (过期)  ')
        return deadline

    def get_submit_deadline(self):
        total_sec = (
            self.get_submit() + datetime.timedelta(
                days=7 * (int(self.week_number_at_submit) + 1)) - datetime.datetime.now(
                util.utc_8)).total_seconds()
        days = int(total_sec / (3600 * 24))
        hours = int((total_sec - 3600 * 24 * days) / 3600)
        submit_deadline = str(days) + '  days,  ' + str(hours) + '  hours'
        if hours < 0:
            submit_deadline += ('  (passdue)  ')
        return submit_deadline

    def get_estimate(self):
        return self.get_submit()+datetime.timedelta(weeks=self.week_number_at_submit    )

    def get_upload(self):
        if self.latest_upload is None:
            return '未上传'
        return self.latest_upload

    def set_upload(self, time):
        self.latest_upload = time

    def get_status(self):
        return int(self.status)

    def get_trans_status(self):
        return int(self.trans_status)

    def get_trans_status_for_translator(self, translator):
        if self.get_status() <= util.SUBMITTED:
            return self.get_trans_status()
        else:
            if translator.get_role() == 1:
                return util.FINISHED
            else:
                return self.get_trans_status()

    def change_status(self, status):
        self.status = status

    def change_trans_status(self, status):
        self.trans_status = status


def order_directory_path(instance, filename):
    return 'order_{0}/{1}/{2}'.format(instance.order.customer.get_name(), instance.order.id, filename)


class Document(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
    description = models.CharField(max_length=50, blank=True)
    required = models.BooleanField(default=False)
    is_origin = models.BooleanField(default=True)
    is_translated = models.BooleanField(default=False)
    is_feedback = models.BooleanField(default=False)
    upload_at = models.DateTimeField(auto_now_add=True)
    comment = models.CharField(max_length=255, blank=True)
    document = models.FileField(upload_to=order_directory_path, null=True)

    class Meta:
        db_table = 'document'

    def get_upload(self):
        return self.upload_at

    def get_name(self):
        return self.document

class Staff(models.Model):
    user = models.OneToOneField(User)
    role = models.IntegerField(default=0)
    sequence = models.DateTimeField(default = timezone.now)

    class Meta:
        db_table = 'auth_staff'
        get_latest_by = 'sequence'

    def get_role(self):
        return int(self.role)

    def get_name(self):
        name = self.user.first_name + ' ' + self.user.last_name
        if name is not ' ':
            return name
        return self.user.username

    def get_assignments(self):  # return order of all assignments
        assignments = []
        if self.get_role() == 1:  # if translator_C2E
            for order in Order.objects.filter(Q(translator_C2E=self.id)).order_by('submit'):
                assignments.append(order)
            return assignments

        if self.get_role() == 2:  # if translator_E2C
            for order in Order.objects.filter(Q(translator_E2C=self.id)).order_by('submit'):
                assignments.append(order)

            return assignments

    def get_assignments_status(self,status):
        assignments = []
        if self.get_role() == 0:
            if status == 'All':
                assignments = list(Order.objects.order_by('submit'))
            else:
                for assignment in Order.objects.order_list.order_by('submit'):

                    if assignment.get_trans_status() == int(status):
                        assignments.append(assignment)
        else:
            for assignment in self.get_assignments():
                if assignment.get_trans_status_for_translator(self) == int(status):
                    assignments.append(assignment)
        return assignments

    def get_assignment_number(self):
        if self.get_role() == 0:
            return 0
        return len(self.get_assignments())

    def set_sequence(self,timestamp):
        self.sequence = timestamp
        self.save()

class Patient(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, default='')
    last_name = models.CharField(max_length=50, default='')
    pin_yin = models.CharField(max_length=50, default='')
    birth = models.DateField(default=datetime.date.today)
    gender = models.CharField(max_length=5, choices=util.GENDER_CHOICES, default=util.MALE)  # birthdate
    category = models.CharField(max_length=50, default='COLD')
    diagnose_hospital = models.CharField(max_length=50, default='')
    doctor = models.CharField(max_length=50, default='')
    relationship = models.CharField(max_length=50, choices=util.RELATION_CHOICES, default=util.SELF)
    passport = models.CharField(max_length=50, default='')
    contact = models.CharField(max_length=50, default='')

    class Meta:
        db_table = 'patient'

    def get_name(self):
        return self.first_name + self.last_name

    def get_age(self):  # method to calculate age
        today = datetime.date.today
        return today.year - self.birth.year - ((today.month, today.day) < (self.birth.month, self.birth.day))


class OrderPatient(models.Model):
    # Order Patient table to store patient information
    # This is created everytime an order is placed
    # Do not change this table when edit patient
    # Fetch patient info for display order-related info
    first_name = models.CharField(max_length=50, default='')
    last_name = models.CharField(max_length=50, default='')
    pin_yin = models.CharField(max_length=50, default='')
    birth = models.DateField(datetime.date.today)
    gender = models.CharField(max_length=5, choices=util.GENDER_CHOICES, default=util.MALE)
    category = models.CharField(max_length=50, default='COLD')
    diagnose_hospital = models.CharField(max_length=50, default='')
    doctor = models.CharField(max_length=50, default='')
    relationship = models.CharField(max_length=50, choices=util.RELATION_CHOICES, default=util.SELF)
    passport = models.CharField(max_length=50, default='')
    contact = models.CharField(max_length=50, default='')

    class Meta:
        db_table = 'order_patient'

    def get_name(self):
        return self.first_name + self.last_name

    def get_age(self):  # method to calculate age
        today = datetime.date.today
        return today.year - self.birth.year - ((today.month, today.day) < (self.birth.month, self.birth.day))


class LikeHospital(models.Model):
    customer = models.ForeignKey(Customer, unique=False, default=None, related_name='customer_liked')
    hospital = models.ForeignKey(Hospital, unique=False, default=None, related_name='hospital_liked')
    disease = models.ForeignKey(Disease, unique=False, default=None, related_name='disease_liked')

    class Meta:
        db_table = 'like_hospital'


class HospitalReview(models.Model):
    hospital = models.ForeignKey(Hospital, unique=False, default=None, related_name='hospital_review')
    order = models.OneToOneField(Order, default=None, related_name='order_review')
    score = models.IntegerField(default=0)
    comment = models.CharField(max_length=200, blank=True)

    class Meta:
        db_table = 'hospital_review'

    def upate_hospital(self):
        self.hospital.update_score(self.score)
