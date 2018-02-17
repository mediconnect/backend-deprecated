#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.files.storage import FileSystemStorage,default_storage
from django.core.signing import Signer,TimestampSigner
from django.contrib.auth.hashers import check_password
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib.sites.shortcuts import get_current_site
from django.core.paginator import Paginator
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.models import User
from customer.models import Customer
from django.apps import apps
from supervisor.forms import (
    TransSignUpForm,ApproveForm,FileForm
)
from django.utils.http import urlsafe_base64_encode
from info import utility as util
from django.http import JsonResponse
from django.template import loader, Context
from django.urls import reverse,reverse_lazy
import json
import csv
import datetime
from django.utils import timezone
from django.http import StreamingHttpResponse
from django.forms.models import model_to_dict
from helper.models import auto_assign,manual_assign
import os
from django.conf import settings
from django.http import HttpResponse,Http404

import urllib
import urlparse
import sys
reload(sys)
sys.setdefaultencoding('utf8')



Order = apps.get_model('helper', 'Order')
Document = apps.get_model('helper', 'Document')
Hospital = apps.get_model('helper', 'Hospital')
Disease = apps.get_model('helper','Disease')
Patient = apps.get_model('helper','Patient')
Patient_Order = apps.get_model('helper','OrderPatient')
Staff = apps.get_model('helper','Staff')
Rank = apps.get_model('helper','Rank')
Questionnaire = apps.get_model('helper','Questionnaire')
Slot = apps.get_model('helper','Slot')
signer = util.signer

"""
Delete Translator Function:
    1. delete translator
    2. delete user
    3. reassign assignment and mark reassigned
"""
@login_required
def validate_pwd(request): # validate password for delete translatoe operation
    data = {
        'validate':False,
        'msg':''
    }
    count = {
        1:0,  # re_assignment success
        -1:0,  # re_assignment failed
        0:0  # re_assignment not needed
    }
    password = request.GET.get('password',None)
    id = request.GET.get('trans_id',None)
    supervisor = Staff.objects.get(user = request.user)
    is_C2E = False
    is_E2C = False
    ERR_NO = 0
    if password is '': # password is empty
        data['msg'] = '密码不能为空'
        return JsonResponse(data)
    if check_password(password,supervisor.user.password):
        data['validate']=True
        translator = Staff.objects.get(user_id=id)
        user = translator.user
        if translator.get_role() == util.TRANS_C2E:
            is_C2E = True
        elif translator.get_role() == util.TRANS_E2C:
            is_E2C = True

        assignments = translator.get_assignments()
        translator.delete()
        user.delete()
        for each in assignments:  # reassign all assignments assigned to the deleted translator
            if each.get_trans_status() <= util.C2E_FINISHED:
                each.c2e_re_assigned += 1
                if is_C2E:
                    ERR_NO = auto_assign(each)
                    count[ERR_NO] += 1
                elif is_E2C:
                    each.set_translator_E2C(None)
                    each.save()
                    count[0] += 1
            else:
                each.e2c_re_assigned += 1
                if is_C2E:
                    each.set_translator_C2E(None)
                    each.save()
                    count[0] += 1
                elif is_E2C:
                    ERR_NO = auto_assign(each)
                    count[ERR_NO] += 1


            each.save()
            data['msg'] = '成功重新分配：' + str(count[1]) + '个文件, '+ '重新分配失败：' + str(count[-1]) + '个文件, '+ '无需分配：' + str(count[0]) + '个文件. '
    else:
        data['msg'] = '密码错误'
        return JsonResponse(data)



    return JsonResponse(data)
"""
Using buffer stream to handle CSV export
    1. Need to format the output
"""
class Echo(object):
    """An object that implements just the write method of the file-like
    interface.
    """
    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value

@login_required
def force_download(request,document_id):
    document = Document.objects.get(id=document_id)
    path = document.document.url
    msg = ''
    file_path = "http://django-env.enc4mpznbt.us-west-2.elasticbeanstalk.com"+path
    debug_path = "http://127.0.0.1:8000"+path
    try:
        response = HttpResponse(document.document,content_type="text/csv")
        response['Content-Disposition'] = 'attachment; filename="{0}"'.format(document.get_name())  # download no need to change
        return response

    except:
        raise Http404



@login_required
def export_csv(request):

    util.log("CSV exported")

    # TODO: Add more log to where database operation is needed;
    # Generate a sequence of rows. The range is based on the maximum number of
    # rows that can be handled by a single sheet in most spreadsheet
    # applications.
    rows = ()
    for each in Order.objects.all():
        rows+=tuple(model_to_dict(each,fields='customer,disease,hospital').items())

    #TODO: Fomrat output csv

    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    response = StreamingHttpResponse((writer.writerow(row) for row in rows),
                                     content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="backup.csv"'#download no need to change

    return response


"""
Ajax function to update the result of home page of supervisor result
    1. Reimplement sorting and filtering function. 
"""


@login_required()
def update_result(request):
    query = request.GET.get('query', None) # handle filter
    search_query = request.GET.get('search_query',None) # handle search
    status = request.GET.get('status', None)
    sort = request.GET.get('sort',None)
    page = request.GET.get('page', 1)
    supervisor = Staff.objects.get(user=request.user)
    raw = supervisor.get_assignments_status(status)  # raw queryset unsorted, unfiltered
    if sort!=None:
        if sort[0] == '-':
            if sort[1:] == 'Deadline':
                raw = reversed(sorted(raw, key=lambda x: x.get_submit_deadline()))
            if sort[1:] == 'Trans_Deadline':
                raw = reversed(sorted(raw, key=lambda x: x.get_deadline()))
            if sort[1:] == 'Upload':
                raw = reversed(sorted(raw, key=lambda x: x.get_upload()))
        else:
            if sort == 'Deadline':
                raw = sorted(raw, key=lambda x: x.get_submit_deadline())
            if sort == 'Trans_Deadline':
                raw = sorted(raw,key = lambda x:x.get_deadline())
            if sort == 'Upload':
                raw = reversed(sorted(raw, key=lambda x: x.get_upload()))
    # translate json to dictionary
    json_acceptable_string = query.replace("'", "\"")
    d = json.loads(json_acceptable_string)
    json_acceptable_string = search_query.replace("'", "\"")
    search_d = json.loads(json_acceptable_string)
    data = {
        'sort_by': sort,
        'choices': {
            'customer_choice': [],
            'patient_choice':[],
            'hospital_choice':[],
            'disease_choice': [],
            'translator_C2E_choice':[],
            'translator_E2C_choice':[],
            'status_choice':[],
            'trans_status_choice':[],
        },
        'message':'Error in order: '

    }
    if search_d == {}:
        data['search_dic'] = {
            'order_id': '',
            'customer': '',
            'patient_order': '',
            'hospital': '',
            'disease': '',
            'translator_C2E': '',
            'translator_E2C': '',
        }
    else:
        data['search_dic'] = search_d
    if d == {}: # initiate the query
        data['dic']={
                  'customer': 'All',
                  'patient_order': 'All',
                  'hospital': 'All',
                  'disease': 'All',
                  'translator_C2E': 'All',
                  'translator_E2C': 'All',
                  'status': 'All',
                  'trans_status': 'All',
              }
    else:
        data['dic'] = d # read and store the query

    if query != None and d != {}:
        result = []
        for each in raw:
            match = True
            for key in d:
                if d[key] != 'All':
                    attr = getattr(each, key)
                    try :
                        int(d[key])
                        try:
                            if attr.id != int(d[key]):
                                 match = False
                                 break
                        except AttributeError:
                           if attr is None:
                               match = False
                               break
                           if int(attr) != int (d[key]):
                               match = False
                               break
                    except ValueError:
                        if str(d[key]) not in str(attr.get_name()):
                            match = False
                            break
            if match:
                result.append(each)
    else:
        result = raw

    if search_query != None and search_d != {}:
        if search_d['order_id']!='':
            try:
                result = [Order.objects.get(id = int(search_d['order_id'])),]
            except Order.DoesNotExist:
                result = []
        else:
            tmp = []
            for each in result:
                match = True
                for key in search_d:
                    if search_d[key] != '':
                        attr = getattr(each,key)
                        if attr!=None:
                            if str(attr.get_name().encode('utf8')).lower().find(str(search_d[key].encode('utf8')).lower())== -1: # support Chinese search
                                match = False
                                break
                        else:
                            match = False
                            break
                if match:
                    tmp.append(each)
            result = tmp

    p = Paginator(result, 5)
    result_length = len(result)
    result = p.page(page)
    data['result_length'] = result_length # pagination
    data['result']={
            'Order_Id': [(-1,'Error')]*len(result),
            'Customer': [(-1,'Error')]*len(result),
            'Patient':[(-1,'Error')]*len(result),
            'Hospital':[(-1,'Error')]*len(result),
            'Disease':[(-1,'Error')]*len(result),
            'Translator_C2E':[(-1,'Error')]*len(result),
            'Translator_E2C':[(-1,'Error')]*len(result),
            'Status': [(-1,'Error')]*len(result),
            'Trans_Status':[(-1,'Error')]*len(result),
            'Deadline':['Error']*len(result),
            'Trans_Deadline':['Error']*len(result),
            'Upload':['Error']*len(result),
            'Link': ['Error']*len(result)
        }

    for x in range(0,len(result)):
        each = result[x]
        try:
            # Latest Upload
            upload = timezone.now()
            if not Document.objects.filter(order_id = each.id).exists():
                upload = 'No upload yet'
            for doc in Document.objects.filter(order_id = each.id):
                if doc.upload_at < upload:
                    upload = doc.upload_at
            data['result']['Order_Id'][x]=each.id
            data['result']['Customer'][x]=((each.customer.id, each.customer.get_name()))
            data['result']['Patient'][x]=(each.get_patient())
            data['result']['Hospital'][x]=((each.hospital.id,each.hospital.name))
            data['result']['Disease'][x]=((each.disease.id, each.disease.name))
            data['result']['Translator_C2E'][x]=(each.get_translator_C2E())
            data['result']['Translator_E2C'][x]=(each.get_translator_E2C())
            data['result']['Status'][x]=((each.get_status(),util.status_dict[int(each.get_status())]))
            data['result']['Trans_Status'][x]=((each.get_trans_status(),util.trans_status_dict[int(each.get_trans_status())]))
            data['result']['Deadline'][x]=(each.get_submit_deadline())
            data['result']['Trans_Deadline'][x]=(each.get_deadline())
            data['result']['Upload'][x]=(upload)
            data['result']['Link'][x]=(reverse('detail', args=[supervisor.user.id, each.id]))
        except Exception as ex:
            template = "\nAn exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            data['message']+='\nID '+str(each.id)+message
    #prepare data for display
    try:
        data['choices']['customer_choice'] = list(map(lambda x:(int(x),Customer.objects.get(id=x).get_name()),Order.objects.values_list('customer_id',flat=True).distinct()))
        data['choices']['disease_choice'] = list(map(lambda x:(int(x),Disease.objects.get(id=x).get_name()),Order.objects.values_list('disease_id',flat=True).distinct()))
        data['choices']['patient_choice'] = list(map(lambda x:(int(x),Patient_Order.objects.get(id=x).get_name()),Order.objects.exclude(patient_order__isnull=True).values_list('patient_order_id',flat=True).distinct()))
        data['choices']['hospital_choice'] = list(map(lambda x:(int(x),Hospital.objects.get(id=x).get_name()),Order.objects.values_list('hospital_id',flat=True).distinct()))
        data['choices']['translator_E2C_choice'] = list(map(lambda x:(x,Staff.objects.get(id=x).get_name()),Order.objects.exclude(translator_E2C__isnull=True).values_list('translator_E2C_id',flat=True).distinct().exclude(translator_E2C__isnull=True)))
        data['choices']['translator_C2E_choice'] = list(map(lambda x:(x,Staff.objects.get(id=x).get_name()),Order.objects.exclude(translator_C2E__isnull=True).values_list('translator_C2E_id',flat=True).distinct().exclude(translator_C2E__isnull=True)))
        data['choices']['status_choice'] = util.STATUS_CHOICES
        data['choices']['trans_status_choice'] = util.TRANS_STATUS_CHOICE
    except:
        data['message']+='\nError in choice'
    return JsonResponse(data)


@login_required
def supervisor(request, id):
    supervisor = Staff.objects.get(user_id=id)
    order_count = len(Order.objects.all())
    customer_count = len(Customer.objects.all())
    trans_C2E_count = len(Staff.objects.filter(role=1))
    trans_E2C_count = len(Staff.objects.filter(role = 2))
    return render(request, 'supervisor_home.html', {
        'supervisor': supervisor,
        'order_count':order_count,
        'customer_count':customer_count,
        'trans_c2e_count':trans_C2E_count,
        'trans_e2c_count':trans_E2C_count
    })

def order_status(request, id,status):
    supervisor = Staff.objects.get(user_id=id)
    return render(request, 'supervisor_order_status.html', {
        'status':status,
        'supervisor': supervisor,
    })


@login_required
def trans_signup(request, id):
    supervisor = Staff.objects.get(user_id=id)
    translators_C2E = Staff.objects.filter(role=1)
    translators_E2C = Staff.objects.filter(role=2)
    if request.method == 'POST':
        form = TransSignUpForm(request.POST)
        if not form.is_valid():
            return render(request, 'trans_signup.html',
                          {'form': form,
                           'supervisor': supervisor,
                           })
        else:
            password = form.cleaned_data.get('password')
            role = form.cleaned_data.get('role')
            email = form.cleaned_data.get('email')
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            User.objects.create_user(username=email, password=password,
                                     email=email, first_name=first_name, last_name=last_name, is_staff=True)
            user = User.objects.get(username = email)
            #login(request, user)
            translator = Staff(user=user,role=role)
            translator.save()
            return render(request, 'translator_list.html',
                          {
                            'translators_C2E': translators_C2E,
                            'translators_E2C': translators_E2C,
                            'supervisor': supervisor
                           })
    else:
        return render(request, 'trans_signup.html',
                      {'form': TransSignUpForm(),
                       'supervisor': supervisor}
                      )



@login_required
def assign(request, id, order_id):
    assignment = Order.objects.get(id=order_id)
    supervisor = Staff.objects.get(user_id=id)
    status = util.status_dict[int(assignment.status)]

    if assignment.get_status() <= util.SUBMITTED: # can reassign C2E translator until submitted to the hospital

        if request.method == 'POST':
            #print request.POST['assignee']
            assignee = Staff.objects.get(user_id = request.POST['assignee'])
            manual_assign(assignment,assignee)

            return render(request, 'detail.html', {
                'assignment': assignment,
                'supervisor': supervisor,
            })
        else:
            C2E_assignee_ids = []
            C2E_assignee_names = []
            for e in Staff.objects.filter(role=1):
                C2E_assignee_names.append((e.user_id,e.get_name()))
            return render(request, 'assign.html', {
                'supervisor': supervisor,
                'assignment': assignment,
                'assignee_names': C2E_assignee_names,
                'assignee_ids': C2E_assignee_ids,
                'status':status
            })
    else:
        if assignment.get_status() <= util.SUBMITTED:  # can reassign C2E translator until submitted to the hospital
            if request.method == 'POST':
                assignee = Staff.objects.get(user_id=request.POST['assignee'])
                manual_assign(assignment, assignee)
                return render(request, 'detail.html', {
                    'assignment': assignment,
                    'supervisor': supervisor,
                })
        else:
            E2C_assignee_ids = []
            E2C_assignee_names = []
            for e in Staff.objects.filter(role = 2):
                E2C_assignee_names.append((e.user_id, e.get_name()))
            return render(request, 'assign.html', {
                'supervisor': supervisor,
                'assignment': assignment,
                'assignee_names': E2C_assignee_names,
                'assignee_ids': E2C_assignee_ids,
                'status':status
            })



def detail(request, id, order_id):
    assignment = Order.objects.get(id=order_id)
    supervisor = Staff.objects.get(user_id=id)
    documents = assignment.get_documents()
    if (request.POST.get('delete')):
        assignment.delete()
        return render(request, 'supervisor_order_status.html', {
            'status': 'All',
            'supervisor': supervisor,
        })
    return render(request, 'detail.html', {
        'assignment': assignment,
        'supervisor': supervisor,
        'documents': documents


    })


@login_required
def approve(request, id, order_id):
    assignment = Order.objects.get(id=order_id)
    supervisor = Staff.objects.get(user_id=id)
    trans_C2E = assignment.translator_C2E
    trans_E2C = assignment.translator_E2C
    customer = Customer.objects.get(id=assignment.customer_id)
    status = util.status_dict[int(assignment.status)]
    documents = assignment.get_documents()
    if request.method == 'POST':
        form = ApproveForm(request.POST)
        if not form.is_valid():
            return render(request, 'approve.html', {
                'form': form,
                'assignment': assignment,
                'supervisor': supervisor
            })
        else:
            approval = form.cleaned_data.get('approval')
            if approval:
                # if approval, change status, trans status, move document from pending to translated
                if assignment.get_status() == util.TRANSLATING_ORIGIN:
                    for document in Document.objects.filter(order_id=assignment.id,
                                                            type=util.C2E_PENDING):  # put all pending documents back to origin
                        document.type = util.C2E_TRANSLATED
                        document.save()
                    assignment.change_status(util.SUBMITTED) # TODO: Supervisor confirm order uploaded to hospital
                    assignment.change_trans_status(util.C2E_FINISHED)

                if assignment.get_status() == util.TRANSLATING_FEEDBACK:
                    for document in Document.objects.filter(order_id=assignment.id,
                                                            type=util.E2C_PENDING):  # put all pending documents back to feedback
                        document.type = util.E2C_TRANSLATED
                        document.save()
                    assignment.change_status(util.FEEDBACK)  # TODO: Customer check order complete function
                    assignment.change_trans_status(util.E2C_FINISHED)

            if not approval:
                #if not approval, change trans status
                if assignment.get_status() == util.TRANSLATING_ORIGIN:
                    assignment.change_trans_status(util.C2E_DISAPPROVED)
                if assignment.get_status() == util.TRANSLATING_FEEDBACK:
                    assignment.change_trans_status(util.E2C_DISAPPROVED)
                assignment.save()
            return render(request, 'detail.html', {
                'assignment': assignment,
                'supervisor': supervisor,
                'status': status,
                'customer': customer,
                'trans_C2E': trans_C2E,
                'trans_E2C': trans_E2C,
                'documents': documents

            })
    else:
        form = ApproveForm()
        return render(request, 'approve.html', {
            'form': form,
            'assignment': assignment,
            'supervisor': supervisor
        })


@login_required
def manage_files(request, id, order_id):
    assignment = Order.objects.get(id=order_id)
    supervisor = Staff.objects.get(user_id=id)
    documents = assignment.get_documents()
    try:

        if (request.POST.get('delete')):
                document = Document.objects.get(document=request.POST.get('document'))
                document_name = document.get_name()
                document.delete()
                msg =  '删除文件'+document_name

                return render(request, 'manage_files.html', {
                    'supervisor': supervisor,
                    'assignment': assignment,
                    'documents': documents,
                    'message':msg
                })
        elif request.method == 'POST' and request.FILES['feedback_files']:
            form = FileForm(request.POST)
            files = request.FILES.getlist('feedback_files')
            document_names = ''
            for file in files:

                document = Document(order=assignment, document=file, type = util.E2C_ORIGIN,description = 'feedback') #create feedback file
                document_names += document.get_name()+','

                #document.save()


            msg = '上传文件'+document_names[:-1]
            if assignment.translator_E2C is None:
                assignment.change_status(util.RETURN)
                auto_assign(assignment)
            assignment.save()
            return render(request, 'manage_files.html', {
                'form':form,
                'supervisor': supervisor,
                'assignment': assignment,
                'documents': documents,
                'msg':msg,
            })
        else:
            form = FileForm()
            return render(request, 'manage_files.html', {
                'form':form,
                'supervisor': supervisor,
                'assignment': assignment,
                'documents': documents,
                'msg': None,
            })
    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:{1!r}"
        msg = template.format(type(ex).__name__, ex.args)
        form = FileForm()
        return render(request, 'manage_files.html', {
            'form':form,
            'supervisor': supervisor,
            'assignment': assignment,
            'documents': documents,
            'msg':msg
        })


@login_required
def send_reset_link(request):
    data = {
        'validate': False,
        'msg': ''
    }
    password = request.GET.get('password', None)
    trans_id = request.GET.get('trans_id',None)
    user = User.objects.get(id = trans_id)
    supervisor = Staff.objects.get(user=request.user)

    if password is '':
        data['msg'] = '密码不能为空'
        return JsonResponse(data)
    if check_password(password, supervisor.user.password):
        data['validate'] = True
    else:
        data['msg'] = '密码错误'
        return JsonResponse(data)

    email_template_name = 'registration/password_reset_email.html'
    from_email = None
    html_email_template_name = None
    subject_template_name = 'registration/password_reset_subject.txt'
    token_generator = default_token_generator
    domain_override = None
    use_https = False
    to_email = user.email
    if not domain_override:
        current_site = get_current_site(request)
        site_name = current_site.name
        domain = current_site.domain
    else:
        site_name = domain = domain_override
    context = {
        'email': user.email,
        'domain': domain,
        'site_name': site_name,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'user': user,
        'token': token_generator.make_token(user),
        'protocol': 'https' if use_https else 'http',
    }

    subject = loader.render_to_string(subject_template_name, context)
    subject = ''.join(subject.splitlines())
    body = loader.render_to_string(email_template_name, context)

    email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
    if html_email_template_name is not None:
        html_email = loader.render_to_string(html_email_template_name, context)
        email_message.attach_alternative(html_email, 'text/html')

    email_message.send()
    return JsonResponse({
        "msg": "Email Sent"
    })

@login_required
def customer_list(request, id):
    supervisor = Staff.objects.get(user_id=id)
    customers = Customer.objects.all()
    return render(request, 'customer_list.html', {
        'customers': customers,
        'supervisor': supervisor
    })



@login_required
def translator_list(request, id):
    supervisor = Staff.objects.get(user_id=id)
    translators_C2E = Staff.objects.filter(role=1)
    translators_E2C = Staff.objects.filter(role=2)
    return render(request, 'translator_list.html', {
        'translators_C2E': translators_C2E,
        'translators_E2C': translators_E2C,
        'supervisor': supervisor,
    })

@login_required
def hospital_list(request, id):
    supervisor = Staff.objects.get(user_id=id)
    hospitals = Hospital.objects.all()
    return render(request, 'hospital_list.html', {
        'hospitals': hospitals,
        'supervisor': supervisor,
    })
@login_required
def set_slots(request):
    hospital = request.GET.get('hospital',None)
    disease = request.GET.get('disease',None)
    slots_dict = request.GET.get('slots_dict',None)
    slots = Slot.objects.get(hospital = hospital,disease = disease)
    if slots_dict != None:
        d = dict(map(lambda (k, v): (int(k), int(v)), json.loads(slots_dict.replace("'", "\"")).iteritems()))
        slots.set_slots(d)
    else:
        slots.set_default_slots()
    data={
        'default':slots.default_slots,
        'week_0': slots.slots_open_0,
        'week_1': slots.slots_open_1,
        'week_2': slots.slots_open_2,
        'week_3': slots.slots_open_3,

    }
    return JsonResponse(data)

@login_required
def rank_manage(request,id):
    supervisor = Staff.objects.get(user = request.user)
    hospital = Hospital.objects.get(id = id)
    disease_detail = Slot.objects.filter(hospital = hospital)

    return render(request,'rank_manage.html',{
        'supervisor':supervisor,
        'hospital':hospital,
        'disease_detail' : disease_detail
    })

@login_required
def check_questionnaire(request,order_id): # check to see if a questionnaire is created/translated
    E2C_assignee_ids = []
    E2C_assignee_names = []
    for e in Staff.objects.filter(role=2):
        E2C_assignee_names.append((e.user_id, e.get_name()))
    supervisor = Staff.objects.get(user = request.user)

    order = Order.objects.get(id = order_id)
    exist = False
    tmp_url=''
    msg=''
    if request.method == 'POST':
        file = request.FILES['origin_pdf']
        translator = Staff.objects.get(user_id=request.POST['translator_E2C'])
        q = Questionnaire.objects.get_or_create(hospital_id=order.hospital_id, disease_id=order.disease_id)[0]
        q.translator = translator
        q.origin_pdf = file
        q.save()
        fs = FileSystemStorage()

        filename = fs.save(file.name,file)
        upload_file_url = fs.url(filename)
        document = Document(order=order, document=upload_file_url, type=util.C2E_ORIGIN,description='origin_pdf')  # upload the answer as an extra doc
        document.save()
        msg = '已上传pdf文件，请等待翻译员创建问卷'
        exist = True
        return render(request, 'check_questionnaire.html', {
            'supervisor': supervisor,
            'order_id': order.id,
            'category': 'unknown',
            'exist': exist,
            'tmp_url': tmp_url,
            'msg': msg
        })
    else:
        try:  # if the questionnaire is already created
            q = Questionnaire.objects.get(hospital_id=order.hospital_id, disease_id=order.disease_id)
            if q.is_translated:  # if is already translated, ready to send link to customer
                tmp_access_key = signer.sign(int(q.id) + int(order_id))
                tmp_url = get_current_site(request).domain+'/core/questionnaire/' + str(q.id) + '/'\
                          + tmp_access_key[(str.find(tmp_access_key,':')) + 1:]
                msg = '问卷已创建并翻译，请直接发送链接至客户邮箱'
            else:
                msg = '问卷已创建，尚未翻译，已分配至英译汉翻译员'
            exist = True
        except Exception as ex:
            exist = False
            template = "\nAn exception of type {0} occurred. Arguments:\n{1!r}"
            msg = template.format(type(ex).__name__, ex.args) # debugging info
        return render(request, 'check_questionnaire.html', {
            'supervisor': supervisor,
            'order_id': order.id,
            'category': 'unknown',
            'exist': exist,
            'tmp_url': tmp_url,
            'msg': msg,
            'assignee_names': E2C_assignee_names,
            'assignee_ids': E2C_assignee_ids,
        })
