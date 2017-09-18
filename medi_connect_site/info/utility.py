# -*- coding: utf-8 -*-
import datetime
from helper.models import Staff
from helper.models import Order


# Function to move the position of a translator in sequence
def auto_assign(order):
    if order.get_status() <= TRANSLATING_ORIGIN:
        assignee = Staff.objects.filter(role=1).order_by('sequence')
        order.set_translator_C2E(assignee)
        order.save()
        assignee.move_to_tail()

    if order.get_status() >= RETURN and order.get_status <= FEEDBACK:
        assignee = Staff.objects.filter(role=2).order_by('sequence')
        order.set_translator_E2C(assignee)
        order.save()
        assignee.move_to_tail()


def manual_assign(order, assignee):
    if order.get_status() <= TRANSLATING_ORIGIN:
        order.set_translator_C2E(assignee)
        order.save()
        assignee.move_to_tail()

    if order.get_status() >= RETURN and order.get_status <= FEEDBACK:
        order.set_translator_E2C(assignee)
        order.save()
        assignee.move_to_tail()


def hospital_directory_path(instance, filename):
    return 'hospital_{0}/{1}'.format(instance.hospital.get_id(), filename)


def order_directory_path(instance, filename):
    return 'order_{0}/{1}/{2}'.format(instance.order.customer.get_name(), instance.order.id, filename)


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

status_dict = ['客户未提交', '客户已提交', '已付款', '原件翻译中', '已提交至医院', '反馈已收到', '反馈翻译中',
               '反馈已上传', '订单完成']
# Trans_status

C2E_NOT_STARTED = 0  # c2e translation not started yet 未开始
C2E_ONGOING = 1  # c2e translation started not submitted to supervisor 翻译中
C2E_APPROVING = 2  # c2e translation submitted to supervisor for approval 审核中
C2E_APPROVED = 4  # c2e translation approved, to status 5 已审核
C2E_DISAPPROVED = 3  # c2e translation disapproved, return to status 1 未批准
C2E_FINISHED = 5  # c2e translation approved and finished for the first half 完成
E2C_NOT_STARTED = 6
E2C_ONGOING = 7
E2C_APPROVING = 8
E2C_APPROVED = 9
E2C_DISAPPROVED = 10
E2C_FINISHED = 11
ALL_FINISHED = 12
TRANS_STATUS_CHOICE = (
    (C2E_NOT_STARTED, 'c2e_not_started'),
    (C2E_ONGOING, 'c2e_ongoing'),
    (C2E_APPROVING, 'c2e_approving'),
    (C2E_APPROVED, 'c2e_approved'),
    (C2E_DISAPPROVED, 'c2e_disapproved'),
    (C2E_FINISHED, 'c2e_finished'),
    (E2C_NOT_STARTED, 'c2e_not_started'),
    (E2C_ONGOING, 'c2e_ongoing'),
    (E2C_APPROVING, 'c2e_approving'),
    (E2C_APPROVED, 'c2e_approved'),
    (E2C_DISAPPROVED, 'c2e_disapproved'),
    (E2C_FINISHED, 'c2e_finished'),
    (ALL_FINISHED, 'all_finished')
)
trans_status_dict = [
    '任务未开始', '翻译中', '提交审核中', '审核驳回', '审核通过', '翻译完成',
    '任务未开始', '翻译中', '提交审核中', '审核驳回', '审核通过', '翻译完成',
    '订单完成'
]

EIGHT = datetime.timedelta(hours=8)


class UTC_8(datetime.tzinfo):
    def utcoffset(self, dt):
        return EIGHT

    def tzname(self, dt):
        return "UTC-8"

    def dst(self, dt):
        return EIGHT


utc_8 = UTC_8()

order_list = Order.objects.all()
