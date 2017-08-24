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

# Trans_status

NOT_STARTED = 0  # assignment not started yet    未开始
ONGOING = 1  # assignment started not submitted to supervisor 进行中
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

trans_status_dict = ['NOT_STARTED', 'ONGOING', 'APPROVING', 'APPROVED', 'DISAPPROVED','FINISHED']

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
        if assignment.get_trans_status() == trans_status:
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
    result_length = len(raw)
    p = Paginator(raw,2)
    raw_page = p.page(page)
    json_acceptable_string = query.replace("'", "\"")
    d = json.loads(json_acceptable_string)
    if query != None and d != {}:
        result = []
        for each in raw_page:
            match = True
            for key in d:
                if d[key] != 'All':
                    attr=getattr(each,key)
                    if attr.id !=int(d[key]):
                        match = False
            if match:
                result.append(each)
    else:
        result = raw_page

    for each in result:
        data['result']['Order_Id'].append(each.id)
        data['result']['Customer'].append((each.customer.id,each.customer.get_name()))
        data['result']['Disease'].append((each.disease.id,each.disease.name))
        data['result']['Submit'].append(each.submit) # submit deadline
        data['result']['Deadline'].append(each.get_remaining()) # translate deadline
        data['result']['Status'].append(each.get_trans_status())
        data['result']['Remaining'].append(each.get_deadline())
        data['result']['Upload'].append(each.get_upload())
        data['result']['Link'].append(reverse('assignment_summary',args=[translator.user.id,each.id]))


    data['choices']['customer_choice']=list(set(data['result']['Customer']))
    data['choices']['disease_choice'] = list(set(data['result']['Disease']))
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
    #assignments = get_assignments_status(translator,status)
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
