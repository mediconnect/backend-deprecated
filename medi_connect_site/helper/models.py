# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.utils import timezone, http

from customer.models import Customer
from info import utility as util


# Function to move the position of a translator in sequence
def auto_assign(order):
    if order.get_status() <= util.TRANSLATING_ORIGIN:
        try:
            assignee = Staff.objects.filter(role=1).order_by('sequence')[0]
            order.set_translator_C2E(assignee)
            order.change_status(util.TRANSLATING_ORIGIN)
            order.change_trans_status(util.C2E_NOT_STARTED)
            assignee.set_sequence(timezone.now())

        except IndexError:
            order.set_translator_C2E(None)

    if order.get_status() >= util.RETURN:
        try:
            assignee = Staff.objects.filter(role=2).order_by('sequence')[0]
            order.set_translator_E2C(assignee)
            order.change_status(util.TRANSLATING_FEEDBACK)
            order.change_trans_status(util.E2C_NOT_STARTED)
            order.auto_assigned = 1
            assignee.set_sequence(timezone.now())

        except IndexError:
            order.set_translator_C2E(None)

    order.save()
    # print order.auto_assigned,order.translator_C2E,order.status,order.trans_status,order.translator_E2C


def manual_assign(order, assignee):
    if order.get_status() <= util.TRANSLATING_ORIGIN:
        order.set_translator_C2E(assignee)
        order.change_status(util.TRANSLATING_ORIGIN)
        order.change_trans_status(util.C2E_NOT_STARTED)
        order.save()
        assignee.set_sequence(timezone.now())

    if order.get_status() >= util.RETURN and order.get_status <= util.FEEDBACK:
        order.set_translator_E2C(assignee)
        order.change_status(util.TRANSLATING_FEEDBACK)
        order.change_trans_status(util.E2C_NOT_STARTED)
        order.save()
        assignee.set_sequence(timezone.now())


class Disease(models.Model):
    name = models.CharField(default='unknown', max_length=50)
    keyword = models.CharField(default='unknown', max_length=150)

    class Meta:
        db_table = 'disease'

    def get_name(self):
        return self.name

    def get_id(self):
        return self.id


class Hospital(models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to=util.hospital_directory_path, null=True)
    email = models.EmailField(blank=True)
    area = models.CharField(blank=True, max_length=50)
    overall_rank = models.IntegerField(default=0)
    website = models.URLField(blank=True)
    introduction = models.TextField(default='intro')
    specialty = models.TextField(default='specialty')
    feedback_time = models.IntegerField(default=1)
    average_score = models.FloatField(null=True)
    review_number = models.IntegerField(blank=True)

    class Meta:
        db_table = 'hospital'

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def update_score(self, score):
        if self.review_number == 0:
            assert self.average_score is None, 'average score is not consistent with review number, something went wrong.'
            self.average_score = score
            self.review_number = 1
        else:
            self.average_score = (self.average_score * self.review_number + score) / (self.review_number + 1)
            self.review_number += 1


class Slot(models.Model):
    hospital = models.ForeignKey('Hospital', on_delete=models.SET_NULL, unique=False, default=None, null=True,
                                 related_name='hospital_slot')
    disease = models.ForeignKey('Disease', on_delete=models.SET_NULL, unique=False, default=None, null=True,
                                related_name='disease_slot')
    default_slots = models.IntegerField(default=20)
    slots_open_0 = models.IntegerField(default=20)
    slots_open_1 = models.IntegerField(default=20)
    slots_open_2 = models.IntegerField(default=20)
    slots_open_3 = models.IntegerField(default=20)

    class Meta:
        db_table = 'slot'

    def reset_slot(self):
        self.slots_open_0 = self.slots_open_1
        self.slots_open_1 = self.slots_open_2
        self.slots_open_2 = self.slots_open_3
        self.slots_open_3 = self.default_slots
        self.save()

    def set_slots(self, slot_dic={}):
        self.default_slots = slot_dic[0]
        self.slots_open_0 = slot_dic[1]
        self.slots_open_1 = slot_dic[2]
        self.slots_open_2 = slot_dic[3]
        self.slots_open_3 = slot_dic[4]
        self.save()


class Price(models.Model):
    hospital = models.ForeignKey('Hospital', unique=False, on_delete=models.SET_NULL, null=True, default=None,
                                 related_name='hospital_price')
    disease = models.ForeignKey('Disease', unique=False, on_delete=models.SET_NULL, null=True, default=None,
                                related_name='disease_price')
    deposit = models.IntegerField(default=10000)
    full_price = models.IntegerField(default=100000)

    class Meta:
        db_table = 'price'


class Rank(models.Model):
    rank = models.IntegerField(default=0)
    hospital = models.ForeignKey('Hospital', unique=False, default=None, on_delete=models.SET_NULL, null=True,
                                 related_name='hospital_rank')
    disease = models.ForeignKey('Disease', unique=False, default=None, on_delete=models.SET_NULL, null=True,
                                related_name='disease_rank')

    class Meta:
        db_table = 'rank'


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    patient = models.ForeignKey('Patient', on_delete=models.SET_NULL, null=True)
    patient_order = models.ForeignKey('OrderPatient', on_delete=models.SET_NULL, null=True)
    translator_C2E = models.ForeignKey('Staff', on_delete=models.SET(1), null=True,
                                       related_name='chinese_translator')  # Translator 1 is reserveed for unassigned
    translator_E2C = models.ForeignKey('Staff', on_delete=models.SET(1), null=True,
                                       related_name='english_translator')
    hospital = models.ForeignKey('Hospital', on_delete=models.SET_NULL, null=True)
    disease = models.ForeignKey('Disease', on_delete=models.SET_NULL, null=True)
    week_number_at_submit = models.IntegerField(default=-1)
    submit = models.DateTimeField(default=timezone.now)  # datetime of receiving the order
    status = models.IntegerField(null=True)
    trans_status = models.CharField(default=0, max_length=20, choices=util.TRANS_STATUS_CHOICE)
    c2e_re_assigned = models.IntegerField(default=0)
    e2c_re_assigned = models.IntegerField(default=0)
    document_complete = models.BooleanField(default=False)
    full_payment_paid = models.BooleanField(default=False)

    class Meta:
        db_table = 'order'

    def get_info(self):
        return 'Order id is ' + str(self.id) + ' Deadline is :' + self.get_deadline()

    def get_translator_C2E(self):
        result = ()
        if self.translator_C2E is None:
            result = (1, '未分配')
        else:
            result = (self.translator_C2E.id, self.translator_C2E.get_name())
        if self.c2e_re_assigned:
            result = (-result[0], result[1])  # if reassigned return negative value

        return result

    def set_translator_C2E(self, assignee):
        self.translator_C2E = assignee
        self.save()

    def get_translator_E2C(self):
        result = ()
        if self.translator_E2C is None:
            result = (1, '未分配')
        else:
            result = (self.translator_E2C.id, self.translator_E2C.get_name())
        if self.e2c_re_assigned:
            result = (-result[0], result[1])  # if reassigned return negative value

        return result

    def set_translator_E2C(self, assignee):
        self.translator_E2C = assignee
        self.save()

    def get_patient(self):
        if self.patient_order is None or self.patient is None:
            return -1, '病人信息缺失'
        else:
            return self.patient_order.id, self.patient_order.get_name()

    def get_submit(self):
        if not self.document_complete:
            return '材料欠缺，无法完成订单'
        return self.submit

    def get_remaining(self):  # deadline for
        return self.submit + datetime.timedelta(weeks=int(self.week_number_at_submit), days=2)

    def get_deadline(self):  # default deadline 2 days after submit time remaining
        total_sec = (self.get_remaining() - datetime.datetime.now(util.utc_8)).total_seconds()
        days = int(total_sec / (3600 * 24))
        hours = int((total_sec - 3600 * 24 * days) / 3600)
        deadline = str(days) + '  天,  ' + str(hours) + '  小时'
        if hours < 0:
            deadline += ('  (过期)  ')
        return deadline

    def get_submit_deadline(self):
        total_sec = (
                self.submit + datetime.timedelta(
            days=7 * (int(self.week_number_at_submit) + 1)) - datetime.datetime.now(
            util.utc_8)).total_seconds()
        days = int(total_sec / (3600 * 24))
        hours = int((total_sec - 3600 * 24 * days) / 3600)
        submit_deadline = str(days) + '  days,  ' + str(hours) + '  hours'
        if hours < 0:
            submit_deadline += ('  (passdue)  ')
        return submit_deadline

    def get_estimate(self):
        if not self.document_complete:
            date = (self.submit + datetime.timedelta(weeks=self.week_number_at_submit,
                                                     days=int(self.hospital.feedback_time),
                                                     hours=8))
        else:
            date = (
                    self.get_submit() + datetime.timedelta(weeks=self.week_number_at_submit,
                                                           days=self.hospital.feedback_time,
                                                           hours=8))
        return str(date.year) + '/' + str(date.month) + '/' + str(date.day) + '-' + str(date.year) + '/' + str(
            date.month) + '/' + str(date.day + 3)

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
        self.save()

    def change_trans_status(self, status):
        self.trans_status = status
        self.save()
 
def order_directory_path(instance, filename):
    return 'order_{0}/{1}/{2}'.format(instance.order.customer.get_name().strip(' '), instance.order.id, http.urlquote(filename))


class Document(models.Model):
    order = models.ForeignKey('Order', on_delete=models.SET_NULL, null=True)
    description = models.CharField(max_length=50, blank=True)
    required = models.BooleanField(default=False)
    upload_at = models.DateTimeField(default=timezone.now)
    document = models.FileField(upload_to=order_directory_path, null=True)
    type = models.IntegerField(default=-1)  # remeber to set the document type when upload

    class Meta:
        db_table = 'document'

    def get_upload(self):
        return self.upload_at

    def get_name(self):
        return self.document


class Staff(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True)
    role = models.IntegerField(default=0)
    sequence = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'auth_staff'

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
            for order in Order.objects.filter(Q(translator_C2E=self.id)).order_by('-id'):
                assignments.append(order)
            return assignments

        if self.get_role() == 2:  # if translator_E2C
            for order in Order.objects.filter(Q(translator_E2C=self.id)).order_by('-id'):
                assignments.append(order)

            return assignments

    def get_assignments_status(self, status):
        assignments = []
        if self.get_role() == 0:
            if status == 'All':
                assignments = list(Order.objects.order_by('-id'))

            elif status == 'PENDING':
                assignments = list(
                    Order.objects.filter(status=util.SUBMITTED).order_by('-id') |
                    Order.objects.filter(status=util.RETURN).order_by('-id'))
            else:
                for assignment in Order.objects.order_by('-id'):
                    if assignment.get_trans_status() == int(status):
                        assignments.append(assignment)
        elif self.get_role() == 1:
            for assignment in self.get_assignments():
                if assignment.get_trans_status_for_translator(self) == int(status):
                    assignments.append(assignment)
            if int(status) == 1:
                for assignment in self.get_assignments():
                    if assignment.get_trans_status_for_translator(self) == util.DISAPPROVED:
                        assignments.append(assignment)
        elif self.get_role() == 2:
            for assignment in self.get_assignments():
                if assignment.get_trans_status_for_translator(self) == int(status) + util.E2C_NOT_STARTED: # use the base status defined in utility
                    assignments.append(assignment)
            if int(status) == 1:
                for assignment in self.get_assignments():
                    if assignment.get_trans_status_for_translator(self) == util.DISAPPROVED:
                        assignments.append(assignment)

        return assignments

    def get_assignment_number(self):
        if self.get_role() == 0:
            return 0
        return len(self.get_assignments())

    def set_sequence(self, timestamp):
        self.sequence = timestamp
        self.save()


class Patient(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    first_name = models.CharField(max_length=50, default=None, null=True)
    last_name = models.CharField(max_length=50, default=None, null=True)
    pin_yin = models.CharField(max_length=50, default=None, null=True)
    birth = models.DateField(default=datetime.date.today, null=True)
    gender = models.CharField(max_length=5, choices=util.GENDER_CHOICES, default=util.MALE)  # birthdate
    category = models.CharField(max_length=50, default=None, null=True)
    diagnose_hospital = models.CharField(max_length=50, default=None, null=True)
    doctor = models.CharField(max_length=50, default=None, null=True)
    relationship = models.CharField(max_length=50, choices=util.RELATION_CHOICES, default=util.SELF)
    passport = models.CharField(max_length=50, default=None, null=True)
    contact = models.CharField(max_length=50, default=None, null=True)

    class Meta:
        db_table = 'patient'

    def get_name(self):
        return self.first_name + ' ' + self.last_name

    def get_age(self):  # method to calculate age
        today = datetime.date.today
        return today.year - self.birth.year - ((today.month, today.day) < (self.birth.month, self.birth.day))


class OrderPatient(models.Model):
    # Order Patient table to store patient nformation
    # This is created everytime an order is placed
    # Do not change this table when edit patient
    # Fetch patient info for display order-related info
    first_name = models.CharField(max_length=50, default=None, null=True)
    last_name = models.CharField(max_length=50, default=None, null=True)
    pin_yin = models.CharField(max_length=50, default=None, null=True)
    birth = models.DateField(datetime.date.today, default=None, null=True)
    gender = models.CharField(max_length=5, choices=util.GENDER_CHOICES, default=util.MALE)
    category = models.CharField(max_length=50, default='COLD')
    diagnose_hospital = models.CharField(max_length=50, default=None, null=True)
    doctor = models.CharField(max_length=50, default=None, null=True)
    relationship = models.CharField(max_length=50, choices=util.RELATION_CHOICES, default=util.SELF)
    passport = models.CharField(max_length=50, default=None, null=True)
    contact = models.CharField(max_length=50, default=None, null=True)

    class Meta:
        db_table = 'order_patient'

    def get_name(self):
        return self.first_name + ' ' + self.last_name

    def get_age(self):  # method to calculate age
        today = datetime.date.today
        return today.year - self.birth.year - ((today.month, today.day) < (self.birth.month, self.birth.day))


class LikeHospital(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, unique=False, default=None, null=True,
                                 related_name='customer_liked')
    hospital = models.ForeignKey('Hospital', on_delete=models.SET_NULL, unique=False, default=None, null=True,
                                 related_name='hospital_liked')
    disease = models.ForeignKey('Disease', on_delete=models.SET_NULL, unique=False, default=None, null=True,
                                related_name='disease_liked')

    class Meta:
        db_table = 'like_hospital'


class HospitalReview(models.Model):
    hospital = models.ForeignKey('Hospital', on_delete=models.SET_NULL, unique=False, default=None, null=True,
                                 related_name='hospital_review')
    order = models.OneToOneField('Order', default=None, on_delete=models.SET_NULL, null=True,
                                 related_name='order_review')
    score = models.IntegerField(default=0)
    comment = models.CharField(max_length=200, blank=True)

    class Meta:
        db_table = 'hospital_review'

    def update_hospital(self):
        self.hospital.update_score(self.score)
        self.save()


class Questionnaire(models.Model):
    hospital = models.ForeignKey('Hospital', on_delete=models.SET_NULL, null=True, unique=False, default=None)
    disease = models.ForeignKey('Disease', on_delete=models.SET_NULL, null=True, unique=False, default=None)
    category = models.CharField(max_length=200, blank=True)
    questions = models.FileField(upload_to=util.questions_path, null=True)
    is_translated = models.BooleanField(default=False)
    translator = models.ForeignKey('Staff', on_delete=models.SET(1), null=False)

    class Meta:
        db_table = 'questionnaire'
