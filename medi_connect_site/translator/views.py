# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.files.storage import FileSystemStorage
from helper.models import UTC_8
from django.db.models import Q
from django.apps import apps
from django.http import JsonResponse
import json
import datetime

# Create your models here.
#Get Order and Document Model from helper.models
Order = apps.get_model('helper','Order')
Document = apps.get_model('helper','Document')
Staff = apps.get_model('helper','Staff')
utc_8 = UTC_8()
# Create your views here.

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

NOT_STARTED = 0  # assignment not started yet    未开始
ONGOING = 1  # assignment started not submitted to supervisor 进行中
APPROVING = 2  # assignment submitted to supervisor for approval
APPROVED = 4  # assignment approved, to status 5
DISAPPROVED = 3  # assignment disapproved, return to status 1
FINISHED = 5  # assignment approved and finished

TRANS_STATUS_CHOICE = (
    (NOT_STARTED, 'not_started'),
    (ONGOING, 'ongoing'),
    (APPROVING, 'approving'),
    (APPROVED, 'approved'),
    (DISAPPROVED, 'disapproved'),
    (FINISHED, 'finished'),
)

trans_status_dict = ['任务未开始', '翻译中', '提交审核中',  '审核驳回','审核通过','翻译完成']

def get_assignments(translator):  # return order of all assignments
    assignments = []
    if translator.get_role() == 1: #if translator_C2E
        for order in Order.objects.filter(Q(translator_C2E=translator.id)).order_by('submit'):

            assignments.append(order)
        return assignments
    if translator.get_role() == 2: #if translator_E2C
        for order in Order.objects.filter(Q(translator_E2C =translator.id)).order_by('submit'):
            assignments.append(order)
        return assignments


def get_assignments_status(translator, trans_status):  # return order of all ongoing assignments
    assignments = []

    for assignment in translator.get_assignments():
        print type(assignment.get_trans_status_for_translator(translator)), int(trans_status)
        if assignment.get_trans_status_for_translator(translator) == int(trans_status):
            assignments.append(assignment)
    return assignments


@login_required()
def update_result(request):
    query=request.GET.get('query',None)
    status = request.GET.get('status',None)
    page = request.GET.get('page',1)
    translator = Staff.objects.get(user=request.user)
    data={
        'result':{
            'Order_Id':[],
            'Customer':[],
            'Disease':[],
            'Submit':[],
            'Deadline':[],
            'Status':[],
            'Remaining':[],
            'Summary':[],
            'Upload':[],
            'Link':[]
        },
        'choices':{
            'customer_choice':[],
            'disease_choice':[]
        },


    }
    raw=get_assignments_status(translator,status)

    json_acceptable_string = query.replace("'", "\"")
    d = json.loads(json_acceptable_string)
    if query != None and d != {}:
        result = []
        for each in raw:
            match = True
            for key in d:
                if d[key] != 'All':
                    attr=getattr(each,key)
                    if attr.id !=int(d[key]):
                        match = False
            if match:
                result.append(each)
    else:
        result = raw

    result_length = len(raw)
    p = Paginator(raw, 5)
    raw_page = p.page(page)

    for each in result:
        data['result']['Order_Id'].append(each.id)
        data['result']['Customer'].append((each.customer.id,each.customer.get_name()))
        data['result']['Disease'].append((each.disease.id,each.disease.name))
        data['result']['Submit'].append(each.get_submit()) # submit deadline
        data['result']['Deadline'].append(each.get_remaining()) # translate deadline
        data['result']['Status'].append(trans_status_dict[int(each.get_trans_status_for_translator(translator))])
        data['result']['Remaining'].append(each.get_deadline())
        data['result']['Upload'].append(each.get_upload())
        data['result']['Link'].append(reverse('assignment_summary',args=[translator.user.id,each.id]))


    data['choices']['customer_choice']=list(set(data['result']['Customer']))
    data['choices']['disease_choice'] = list(set(data['result']['Disease']))
    data['result_length']=result_length
    return JsonResponse(data,safe=False)

@login_required
def translator(request, id):
    translator = Staff.objects.get(user_id = id)

    return render(request, 'trans_home.html',
                  {
                      'translator': translator,
                  })

@login_required
def translator_status(request,id,status):
    translator = Staff.objects.get(user_id = id)
    return render(request,'trans_home_status.html',
                  {
                      'status':status,
                      'translator':translator
                  })
@login_required
def assignment_summary(request, id, order_id):
    translator = Staff.objects.get(user_id = id)
    assignment = Order.objects.get(id=order_id)
    if (request.POST.get('accept')):
        if translator.get_role() == 1:
            assignment.change_status(TRANSLATING_ORIGIN)
        if translator.get_role() == 2:
            assignment.change_status(TRANSLATING_FEEDBACK)
        assignment.change_trans_status(ONGOING)
        assignment.save()
        return render(request, 'assignment_summary.html', {
            'translator': translator,
            'assignment': assignment
        })
    if(request.POST.get('approval')):
        assignment.change_trans_status(APPROVING)
        assignment.save()
        return render(request, 'assignment_summary.html', {
            'translator': translator,
            'assignment': assignment
        })
    if (request.POST.get('finish')):
        assignment.change_trans_status(FINISHED)
        assignment.save()
        return render(request, 'assignment_summary.html', {
            'translator': translator,
            'assignment': assignment
        })
    if (request.POST.get('redo')):
        assignment.change_trans_status(ONGOING)
        assignment.save()
        return render(request, 'assignment_summary.html', {
            'translator': translator,
            'assignment': assignment
        })
    if request.method == 'POST' and request.FILES.get('trans_files',False):
        file = request.FILES['trans_files']
        fs = FileSystemStorage()
        filename = fs.save(file.name, file)
        document = Document(order=assignment, document=file, is_origin=False)
        document.save()
        assignment.pending.add(document)
        assignment.set_upload(datetime.datetime.now(utc_8))
        assignment.save()
        return render(request, 'assignment_summary.html', {
            'translator': translator,
            'assignment': assignment
        })

    else:

        return render(request, 'assignment_summary.html', {
            'translator': translator,
            'assignment': assignment
        })
