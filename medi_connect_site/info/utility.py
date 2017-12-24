# -*- coding: utf-8 -*-
# ======This file can only contain non-order dependant functions======#
import datetime
import logging

# Standard instance of a logger with __name__
stdlogger = logging.getLogger('mediconnect')
# Custom instance logging with explicit name
dbalogger = logging.getLogger('dba')


def index():
    stdlogger.debug("Entering index method")


def log(msg):
    stdlogger.debug(msg)


def hospital_directory_path(instance, filename):
    return 'hospital_{0}/{1}'.format(instance.hospital.get_id(), filename)


def order_directory_path(instance, filename):
    return 'order_{0}/{1}/{2}'.format(instance.order.customer.get_name(), instance.order.id, filename)


def questions_path(instance, filename):
    return 'hospital_{0}/disease_{1}/{2}'.format(instance.hospital.get_id(), instance.disease.get_id(), filename)


# Gender
MALE = 'M'
FEMALE = 'F'

GENDER_CHOICES = (
    (MALE, 'Male'),
    (FEMALE, 'Female'),
    ('OTHER', 'Other')
)
# Relation
# 本人，父母，子女，配偶，其他亲属，朋友，其他
SELF = 'SELF'
PARENT = 'PARENT'
CHILD = 'CHILD'
SPOUSE = 'SPOUSE'
RELATIVE = 'RELATIVE'
FRIEND = 'FRIEND'
OTHER = 'OTHER'
RELATION_CHOICES = (
    (SELF, '本人'),
    (PARENT, '父母'),
    (CHILD, '子女'),
    (SPOUSE, '配偶'),
    (RELATIVE, '其他亲属'),
    (FRIEND, '朋友'),
    (OTHER, '其他')
)

# Status
STARTED = 0  # 下单中
PAID = 1  # order paid 已付款
TRANSLATING_ORIGIN = 2  # translator starts translating origin documents 翻译原件中
SUBMITTED = 3  # origin documents translated, approved and submitted to hospitals 已提交
# ============ Above is C2E status =============#
# ============Below is E2C status ==============#
RETURN = 4  # hospital returns feedback
TRANSLATING_FEEDBACK = 5  # translator starts translating feedback documents 翻译反馈中
FEEDBACK = 6  # feedback documents translated, approved, and feedback to customer 已反馈
DONE = 7  # customer confirm all process done 完成

STATUS_CHOICES = (
    (STARTED, 'started'),
    (SUBMITTED, 'submitted'),
    (TRANSLATING_ORIGIN, 'translating_origin'),
    (RETURN, 'return'),
    (TRANSLATING_FEEDBACK, 'translating_feedback'),
    (FEEDBACK, 'feedback'),
    (PAID, 'PAID'),
)

status_dict = ['客户未提交', '已付款', '原件翻译中', '提交至医院', '上传反馈', '反馈翻译中',
               '反馈已上传', '订单完成']
# Trans_status
# Temporarily hold status

C2E_NOT_STARTED = 0  # c2e translation not started yet 未开始
C2E_ONGOING = 1  # c2e translation started not submitted to supervisor 翻译中
C2E_APPROVING = 2  # c2e translation submitted to supervisor for approval 审核中
C2E_APPROVED = 4  # c2e translation approved, to status 5 已审核
C2E_DISAPPROVED = 3  # c2e translation disapproved, return to status 1 未批准
C2E_FINISHED = 5  # c2e translation approved and finished for the first half 完成

NOT_STARTED = C2E_NOT_STARTED
ONGOING = C2E_ONGOING
APPROVING = C2E_APPROVING
APPROVED = C2E_APPROVED
DISAPPROVED = C2E_DISAPPROVED
FINISHED = C2E_FINISHED

E2C_NOT_STARTED = 6
E2C_ONGOING = 7
E2C_APPROVING = 8
E2C_APPROVED = 10
E2C_DISAPPROVED = 9
E2C_FINISHED = 11
ALL_FINISHED = 12
TRANS_STATUS_CHOICE = (
    (C2E_NOT_STARTED, '汉译英未开始'),
    (C2E_ONGOING, '汉译英进行中'),
    (C2E_APPROVING, '汉译英审核中'),
    (C2E_APPROVED, '汉译英已审核'),
    (C2E_DISAPPROVED, '汉译英驳回'),
    (C2E_FINISHED, '汉译英已完成'),
    (E2C_NOT_STARTED, '英译汉未开始'),
    (E2C_ONGOING, '英译汉进行中'),
    (E2C_APPROVING, '汉译英审核中'),
    (E2C_APPROVED, '汉译英已审核'),
    (E2C_DISAPPROVED, '汉译英驳回'),
    (E2C_FINISHED, '汉译英已完成'),
    (ALL_FINISHED, '订单完成')
)
trans_status_dict = [
    '任务未开始', '翻译中', '提交审核中', '审核驳回', '审核通过', '翻译完成',
    '任务未开始', '翻译中', '提交审核中', '审核驳回', '审核通过', '翻译完成',
    '订单完成'
]

# Questionnaire formats
MULTIPLE_CHOICE = 0
CHOOSE_ONE = 1
TEXT = 2

FORMAT_CHOICE = (
    (MULTIPLE_CHOICE, '多项选择'),
    (CHOOSE_ONE, '单选'),
    (TEXT, '简答')
)

EIGHT = datetime.timedelta(hours=8)


class UTC_8(datetime.tzinfo):
    def utcoffset(self, dt):
        return EIGHT

    def tzname(self, dt):
        return "UTC-8"

    def dst(self, dt):
        return EIGHT


utc_8 = UTC_8()

# Payment Status
NOT_PAID = 0
DEPOSIT_PAID = 1
FULL_PAYMENT = 2
