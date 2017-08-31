# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q
import datetime
from customer.models import Customer


# Function to move the position of a translator in sequence
def move(trans_list, translator_id, new_position):
    old_position = trans_list.index(translator_id)
    trans_list.insert(new_position, trans_list.pop(old_position))
    return trans_list


class Disease(models.Model):
    name = models.CharField(default='unknown', max_length=50)
    keyword = models.CharField(default='unknown', max_length=150)

    class Meta:
        db_table = 'disease'

    def get_name(self):
        return self.name

def hospital_directory_path(instance, filename):
    return 'hospital_{0}/{1}'.format(instance.hospital.get_name(),filename)

class Hospital(models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to=hospital_directory_path,null=True)
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
    average_score = models.FloatField(null = True)
    review_number = models.IntegerField(default = 0)

    class Meta:
        db_table = 'hospital'

    def get_name(self):
        return self.name

    def reset_slot(self):
        self.slots_open_0 = self.slots_open_1
        self.slots_open_1 = self.slots_open_2
        self.slots_open_2 = self.slots_open_3
        self.slots_open_3 = self.default_slots
        self.save()

    def set_default_slots(self, slot):
        self.default_slots = slot
        self.slots_open_0 = self.default_slots
        self.slots_open_1 = self.default_slots
        self.slots_open_2 = self.default_slots
        self.slots_open_3 = self.default_slots

    def update_score(self,score):
        if self.review_number == 0:
            assert self.average_score is None, 'average score is not consistent with review number, something went wrong.'
            self.average_score = score
            self.review_number = 1
        else:
            self.average_score = (self.average_score*self.review_number+score)/(self.review_number+1)
            self.review_number += 1


class Rank(models.Model):
    rank = models.IntegerField(default=0)
    hospital = models.ForeignKey(Hospital, unique=False, default=None, related_name='hospital_rank')
    disease = models.ForeignKey(Disease, unique=False, default=None, related_name='disease_rank')

    class Meta:
        db_table = 'rank'


# Status
STARTED = 0  # 下单中
PAID = 1  # paid 已付款
RECEIVED = 2  # order received 已接单
TRANSLATING_ORIGIN = 3  # translator starts translating origin documents 翻译原件中
SUBMITTED = 4  # origin documents translated, approved and submitted to hospitals 已提交
# ============ Above is C2E status =============#
# ============Below is E2C status ==============#
RETURN = 5  # hospital returns feedback
TRANSLATING_FEEDBACK = 6  # translator starts translating feedback documents 翻译反馈中
FEEDBACK = 7  # feedback documents translated, approved, and feedback to customer 已反馈
DONE = 8  # customer confirm all process done 完成

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

status_dict = ['客户未提交', '客户已提交','已付款',  '原件翻译中', '已提交至医院', '反馈已收到', '反馈翻译中',
               '反馈已上传', '订单完成']
# Trans_status

NOT_STARTED = 0  # assignment not started yet 未开始
ONGOING = 1  # assignment started not submitted to supervisor 翻译中
APPROVING = 2  # assignment submitted to supervisor for approval 审核中
APPROVED = 4  # assignment approved, to status 5 已审核
DISAPPROVED = 3  # assignment disapproved, return to status 1 未批准
FINISHED = 5  # assignment approved and finished for the first half 完成
ALL_FINISHED = 6 #All done
TRANS_STATUS_CHOICE = (
    (NOT_STARTED, 'not_started'),
    (ONGOING, 'ongoing'),
    (APPROVING, 'approving'),
    (APPROVED, 'approved'),
    (DISAPPROVED, 'disapproved'),
    (FINISHED, 'finished'),
    (ALL_FINISHED,'all_finished')
)

trans_status_dict = ['任务未开始', '翻译中', '提交审核中', '审核驳回','审核通过','翻译完成','订单完成']

EIGHT = datetime.timedelta(hours=8)


class UTC_8(datetime.tzinfo):
    def utcoffset(self, dt):
        return EIGHT

    def tzname(self, dt):
        return "UTC-8"

    def dst(self, dt):
        return EIGHT


utc_8 = UTC_8()


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True)
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE, null=True)
    # keep the website working, change this after change all patient related information
    patient_order = models.ForeignKey('OrderPatient', on_delete=models.CASCADE, null=True)
    # translator Chinese to English
    translator_C2E = models.ForeignKey('Staff', on_delete=models.CASCADE, null=True,
                                       related_name='chinese_translator')
    # translator English to Chinese
    translator_E2C = models.ForeignKey('Staff', on_delete=models.CASCADE, null=True,
                                       related_name='english_translator')
    # supervisor = models.ForeignKey(Supervisor, on_delete = models.CASCADE, null = True)
    # only one supervisor for now, no need to keep this info
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
    status = models.CharField(blank=True, max_length=20, choices=STATUS_CHOICES)
    trans_status = models.CharField(default=0, max_length=20, choices=TRANS_STATUS_CHOICE)
    auto_assigned = models.BooleanField(default=False)
    step = models.IntegerField(null=True)

    class Meta:
        db_table = 'order'

    def get_info(self):
        return 'Order id is ' + str(self.id) + ' Deadline is :' + self.get_deadline()

    def get_translator_C2E(self):
        if self.translator_C2E is None:
            return(-1,'未分配')
        else:
            return(self.translator_C2E.id,self.translator_C2E.get_name())

    def get_translator_E2C(self):
        if self.translator_E2C is None:
            return(-1,'未分配')
        else:
            return(self.translator_E2C.id,self.translator_E2C.get_name())

    def get_submit(self):
        return self.submit   + datetime.timedelta(hours = 8)

    def get_remaining(self):  # deadline
        return self.get_submit() + datetime.timedelta(days=2);


    def get_deadline(self):  # default deadline 2 days after submit time remaining
        total_sec = (self.get_submit() + datetime.timedelta(days=2) - datetime.datetime.now(utc_8)).total_seconds()
        days = int(total_sec / (3600 * 24))
        hours = int((total_sec - 3600 * 24 * days) / 3600)
        deadline = str(days) + '  天,  ' + str(hours) + '  小时'
        if hours < 0:
            deadline += ('  (过期)  ')
        return deadline

    def get_submit_deadline(self):
        total_sec = (self.get_submit() + datetime.timedelta(days=7 * (int(self.week_number_at_submit) + 1)) - datetime.datetime.now(utc_8)).total_seconds()
        days = int(total_sec / (3600 * 24))
        hours = int((total_sec - 3600 * 24 * days) / 3600)
        submit_deadline = str(days) + '  days,  ' + str(hours) + '  hours'
        if hours < 0:
            submit_deadline += ('  (passdue)  ')
        return submit_deadline

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

    def get_trans_status_for_translator(self,translator):
        if self.get_status()<= SUBMITTED :
            return self.get_trans_status()
        else:
            if translator.get_role() == 1:
                return FINISHED
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
    is_feedback = models.BooleanField(default = False)
    upload_at = models.DateTimeField(auto_now_add=True)
    comment = models.CharField(max_length=255, blank=True)
    document = models.FileField(upload_to=order_directory_path, null=True)

    class Meta:
        db_table = 'document'

    def get_upload(self):
        return self.upload_at


class Staff(models.Model):
    user = models.OneToOneField(User)
    role = models.IntegerField(default=0)

    # sequence = models.IntegerField(unique=True)

    class Meta:
        db_table = 'auth_staff'

    def get_role(self):
        return self.role

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

    def get_document_number(self):
        count = 0
        if self.get_role() == 1:  # if translator_C2E
            for e in self.get_assignments():
                count += e.origin.count()
        if self.get_role() == 2:
            for e in self.get_assignments():
                count += e.feedback.count()
        return count


trans_list_C2E = list(Staff.objects.filter(role=1).values_list('id', flat=True))
trans_list_E2C = list(Staff.objects.filter(role=2).values_list('id', flat=True))

# Gender
MALE = 'M'
FEMALE = 'F'

GENDER_CHOICES = (
    (MALE, 'Male'),
    (FEMALE, 'Female'),
    ('OTHER', 'Other')
)
# Relation
SELF = 'SELF'
RELATIVE = 'RELATIVE'
CLIENT = 'CLIENT'
RELATION_CHOICES = (
    (SELF, 'SELF'),
    (RELATIVE, 'RELATIVE'),
    (CLIENT, 'CLIENT')
)


class Patient(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    name = models.CharField(blank=True, max_length=50)
    age = models.IntegerField(blank=True)
    gender = models.CharField(max_length=5, choices=GENDER_CHOICES, default=MALE)
    category = models.CharField(max_length=50, default='COLD')
    diagnose_hospital = models.CharField(max_length=50, blank=True)
    doctor = models.TextField(blank=True)
    relationship = models.CharField(max_length=50, choices=RELATION_CHOICES, default=SELF)

    class Meta:
        db_table = 'patient'

    def get_name(self):
        return self.name

class OrderPatient(models.Model):
    # Order Patient table to store patient information
    # This is created everytime an order is placed
    # Do not change this table when edit patient
    # Fetch patient info for display order-related info
    name = models.CharField(blank=True, max_length=50)
    age = models.IntegerField(blank=True)
    gender = models.CharField(max_length=5, choices=GENDER_CHOICES, default=MALE)
    category = models.CharField(max_length=50, default='COLD')
    diagnose_hospital = models.CharField(max_length=50, blank=True)
    doctor = models.TextField(blank=True)
    relationship = models.CharField(max_length=50, choices=RELATION_CHOICES, default=SELF)
    class Meta:
        db_table = 'order_patient'

    def get_name(self):
        return self.name

class LikeHospital(models.Model):
    customer = models.ForeignKey(Customer, unique=False, default=None, related_name='customer_liked')
    hospital = models.ForeignKey(Hospital, unique=False, default=None, related_name='hospital_liked')
    disease = models.ForeignKey(Disease, unique=False, default=None, related_name='disease_liked')

    class Meta:
        db_table = 'like_hospital'


class HospitalReview(models.Model):
    hospital = models.ForeignKey(Hospital, unique=False, default=None, related_name='hospital_review')
    order = models.OneToOneField(Order,default = None, related_name='order_review')
    score = models.IntegerField()
    comment = models.CharField(max_length=200,blank=True)

    class Meta:
        db_table = 'hospital_review'

    def upate_hospital(self):
        self.hospital.update_score(self.score)