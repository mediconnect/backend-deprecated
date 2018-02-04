# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.shortcuts import render,redirect
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.files.storage import FileSystemStorage
from info import utility as util
from forms import StaffLoginForm
from django.contrib.auth import authenticate, login
from django.db.models import Q
from django.apps import apps
from django.http import JsonResponse
import json
import datetime
from django.utils import timezone
import os
import re
from django.conf import settings
from django.http import HttpResponse,Http404
import urllib

# Create your models here.
#Get Order and Document Model from helper.models
Order = apps.get_model('helper','Order')
Document = apps.get_model('helper','Document')
Staff = apps.get_model('helper','Staff')
Hospital = apps.get_model('helper','Hospital')
Dynamic_Form = apps.get_model('dynamic_form','DynamicForm')
utc_8 = util.UTC_8()

# Create your views here.

def translator_auth(request):
    # TODO: add more eror info
    if request.method == 'POST':
        form = StaffLoginForm(request.POST)
        if not form.is_valid():
            return render(request, 'trans_login.html',
                          {'form': form})
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')
        user = authenticate(email=email, password=password)
        if user is None:
            return render(request, 'trans_login.html',
                          {'form': form})
        login(request, user)
        translator = Staff.objects.get(user=user)
        return render(request, 'trans_home.html',
                      {
                          'translator': translator,
                      })
    return render(request, 'trans_login.html', {
        'form': StaffLoginForm()
    })

@login_required
def force_download(request,document_id):
    document = Document.objects.get(id=document_id)
    path = document.document.url
    file_path = "http://django-env.enc4mpznbt.us-west-2.elasticbeanstalk.com"+path
    debug_path = "http://127.0.0.1:8000"+path
    response = HttpResponse(document.document,content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="{0}"'.format(document.get_name())  # download no need to change
    return response
    """
    if os.path.exists(debug_path):
        with open(debug_path,'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/liquid",charset = 'utf-8')
            response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(debug_path.encode('utf-8'))
            return response
    """

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
    raw=translator.get_assignments_status(status)
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
        # Latest Upload
        upload = timezone.now()
        for doc in Document.objects.filter(order_id=each.id):
            if doc.upload_at < upload:
                upload = doc.upload_at
        data['result']['Order_Id'].append(each.id)
        data['result']['Customer'].append((each.customer.id,each.customer.get_name()))
        data['result']['Disease'].append((each.disease.id,each.disease.name))
        data['result']['Submit'].append(each.get_submit()) # submit deadline
        data['result']['Deadline'].append(each.get_remaining()) # translate deadline
        data['result']['Status'].append(util.trans_status_dict[int(each.get_trans_status_for_translator(translator))])
        data['result']['Remaining'].append(each.get_deadline())
        data['result']['Upload'].append(upload)
        data['result']['Link'].append(reverse('assignment_summary',args=[translator.user.id,each.id]))


    data['choices']['customer_choice']=list(set(data['result']['Customer']))
    data['choices']['disease_choice'] = list(set(data['result']['Disease']))
    data['result_length']=result_length
    return JsonResponse(data,safe=False)



@login_required
def translator(request, id):
    translator = Staff.objects.get(user_id = id)
    order_count = {
        '未开始任务':len(translator.get_assignments_status(util.NOT_STARTED)),
        '翻译中任务':len(translator.get_assignments_status(util.ONGOING)),
        '等待审核':len(translator.get_assignments_status(util.APPROVING))
    }

    return render(request, 'trans_home.html',
                  {
                      'order_count':order_count,
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
    hospital = Hospital.objects.get(id = assignment.hospital_id )
    dynamic_form = Dynamic_Form.objects.get(hospital_id = hospital.id,disease_id = assignment.disease_id)
    types = dynamic_form.form
    if translator.get_role() == util.TRANS_C2E:
        origin_documents = Document.objects.filter(order_id = order_id,type = 0 )
        pending_documents = Document.objects.filter(order_id = order_id, type = 1)
        types_list = filter(lambda x: x.isalpha(), re.split(r'[ ;|,\s]\s*', str(types)))
    if translator.get_role() == util.TRANS_E2C:
        origin_documents = Document.objects.filter(order_id = order_id, type = 3)
        pending_documents = Document.objects.filter(order_id = order_id, type = 4)
        types_list = ['feedback']
    if (request.POST.get('accept')):
        if translator.get_role() == 1:
            assignment.change_status(util.TRANSLATING_ORIGIN)
            assignment.change_trans_status(util.C2E_ONGOING)
        if translator.get_role() == 2:
            assignment.change_status(util.TRANSLATING_FEEDBACK)
            assignment.change_trans_status(util.E2C_ONGOING)
        assignment.save()

    if(request.POST.get('approval')):
        if translator.get_role() == 1:
            assignment.change_trans_status(util.C2E_APPROVING)
        if translator.get_role() == 2:
            assignment.change_trans_status(util.E2C_APPROVING)
        assignment.save()

    if (request.POST.get('finish')):
        if translator.get_role() == 1:
            assignment.change_trans_status(util.C2E_FINISHED)
        if translator.get_role() == 2:
            assignment.change_trans_status(util.E2C_FINISHED)
        assignment.save()

    if (request.POST.get('redo')):
        if translator.get_role() == 1:
            assignment.change_trans_status(util.C2E_ONGOING)
        if translator.get_role() == 2:
            assignment.change_trans_status(util.E2C_ONGOING)
        assignment.save()

    if (request.POST.get('upload')):

        for type in types_list:
            print 'trans_files_' + type
            if 'trans_files_'+type in request.FILES is not None:

                file = request.FILES['trans_files_'+type]

                if translator.get_role() == util.TRANS_C2E:
                    document = Document(order=assignment, document=file,
                                        type=util.C2E_PENDING,description = 'trans_files_'+type)  # upload to pending documents
                if translator.get_role() == util.TRANS_E2C:
                    document = Document(order=assignment, document=file, type=util.E2C_PENDING,description= 'trans_files_'+type)

                document.save()

                assignment.save()



    return render(request, 'assignment_summary.html', {
        'origin_documents': origin_documents,
        'pending_documents': pending_documents,
        'translator': translator,
        'assignment': assignment,
        'types': types_list

    })
