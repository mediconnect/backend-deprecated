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

# Create your models here.
#Get Order and Document Model from helper.models
Order = apps.get_model('helper','Order')
Document = apps.get_model('helper','Document')
Staff = apps.get_model('helper','Staff')
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
    order_count = len(translator.get_assignments())
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
    if translator.get_role() == util.TRANS_C2E:
        origin_documents = Document.objects.filter(order_id = order_id,type = 0 )
        pending_documents = Document.objects.filter(order_id = order_id, is_translated = 1)
    if translator.get_role() == util.TRANS_E2C:
        origin_documents = Document.objects.filter(order_id = order_id, type = 3)
        pending_documents = Document.objects.filter(order_id = order_id, type = 4)
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

    if request.method == 'POST' and request.FILES.get('trans_files',False):
        file = request.FILES['trans_files']
        fs = FileSystemStorage()
        filename = fs.save(file.name, file)
        document = Document(order=assignment, document=file, is_translated=True,type = 1) #upload to pending documents
        document.save()
        assignment.set_upload(datetime.datetime.now(utc_8))
        assignment.save()

    return render(request, 'assignment_summary.html', {
        'origin_documents': origin_documents,
        'pending_documents': pending_documents,
        'translator': translator,
        'assignment': assignment
    })
