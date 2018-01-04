# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core import serializers
from django.core.files.storage import FileSystemStorage,default_storage
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
    TransSignUpForm,ApproveForm,GenerateQuestionnaireForm,ChoiceForm
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
from django.core.files.base import ContentFile
from helper.models import auto_assign,manual_assign


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
    password = request.GET.get('password',None)
    id = request.GET.get('trans_id',None)
    supervisor = Staff.objects.get(user = request.user)
    if password is '': # password is empty
        data['msg'] = '密码不能为空'
        return JsonResponse(data)
    if check_password(password,supervisor.user.password):
        data['validate']=True
    else:
        data['msg'] = '密码错误'
        return JsonResponse(data)

    translator = Staff.objects.get(user_id = id)
    user = translator.user
    assignments = translator.get_assignments()
    translator.delete()
    user.delete()
    for each in assignments: # reassign all assignments assigned to the deleted translator
        if each.get_status() <= util.C2E_FINISHED:
            each.c2e_reassigned += 1
        else:
            each.c2e_reassigned += 1
        auto_assign(each)
        each.save()
    data['msg']='操作成功' # return success only in reassign succeed

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
    query = request.GET.get('query', None)
    status = request.GET.get('status', None)
    sort = request.GET.get('sort',None)
    page = request.GET.get('page', 1)
    supervisor = Staff.objects.get(user=request.user)

    data = {
        'sort_by': 'None',
        'result': {
            'Order_Id': [],
            'Customer': [],
            'Patient':[],
            'Hospital':[],
            'Disease':[],
            'Translator_C2E':[],
            'Translator_E2C':[],
            'Status': [],
            'Trans_Status':[],
            'Deadline':[],
            'Trans_Deadline':[],
            'Upload':[],
            'Link': []
        },
        'choices': {
            'customer_choice': [],
            'patient_choice':[],
            'hospital_choice':[],
            'disease_choice': [],
            'translator_C2E_choice':[],
            'translator_E2C_choice':[],
            'status_choice':[],
            'trans_status_choice':[],
        }

    }
    raw = supervisor.get_assignments_status(status) # raw queryset unsorted, unfiltered

    if sort!=None:
        if sort == 'Deadline':
            raw = sorted(raw, key=lambda x: x.get_submit_deadline())
        if sort == 'Trans_Deadline':
            raw = sorted(raw,key = lambda x:x.get_deadline())
        if sort == 'Upload':
            raw = sorted(raw,key = lambda x:x.get_upload())


    json_acceptable_string = query.replace("'", "\"")
    d = json.loads(json_acceptable_string)
    if d == {}: # initiate the query
        data['dic']={
                  'order_id': 'All',
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
    if d!={} and d['order_id']!= 'All': #get one specific order using order id
        result = [Order.objects.get(id=d['order_id'])]
    else: # filter the queryset using the query exact match
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

    p = Paginator(result, 5)
    result_length = len(result)
    result = p.page(page)
    data['result_length'] = result_length #pagination



    for each in result:
        # Latest Upload
        upload = timezone.now()
        if not Document.objects.filter(order_id = each.id).exists():
            upload = 'No upload yet'
        for doc in Document.objects.filter(order_id = each.id):
            if doc.upload_at < upload:
                upload = doc.upload_at

        data['result']['Order_Id'].append(each.id)
        data['result']['Customer'].append((each.customer.id, each.customer.get_name()))
        data['result']['Patient'].append(each.get_patient())
        data['result']['Hospital'].append((each.hospital.id,each.hospital.name))
        data['result']['Disease'].append((each.disease.id, each.disease.name))
        data['result']['Translator_C2E'].append(each.get_translator_C2E())
        data['result']['Translator_E2C'].append(each.get_translator_E2C())
        data['result']['Status'].append((each.get_status(),util.status_dict[int(each.get_status())]))
        data['result']['Trans_Status'].append((each.get_trans_status(),util.trans_status_dict[int(each.get_trans_status())]))
        data['result']['Deadline'].append(each.get_submit_deadline())
        data['result']['Trans_Deadline'].append(each.get_deadline())
        data['result']['Upload'].append(upload)
        data['result']['Link'].append(reverse('detail', args=[supervisor.user.id, each.id]))
    #prepare data for display
    data['choices']['customer_choice'] = list(map(lambda x:(int(x),Customer.objects.get(id=x).get_name()),Order.objects.values_list('customer_id',flat=True).distinct()))
    data['choices']['disease_choice'] = list(map(lambda x:(int(x),Disease.objects.get(id=x).get_name()),Order.objects.values_list('disease_id',flat=True).distinct()))
    data['choices']['patient_choice'] = list(map(lambda x:(int(x),Patient_Order.objects.get(id=x).get_name()),Order.objects.exclude(patient_order__isnull=True).values_list('patient_order_id',flat=True).distinct()))
    data['choices']['hospital_choice'] = list(map(lambda x:(int(x),Hospital.objects.get(id=x).get_name()),Order.objects.values_list('hospital_id',flat=True).distinct()))
    data['choices']['translator_E2C_choice'] = list(map(lambda x:(x,Staff.objects.get(id=x).get_name()),Order.objects.exclude(translator_E2C__isnull=True).values_list('translator_E2C_id',flat=True).distinct().exclude(translator_E2C__isnull=True)))
    data['choices']['translator_C2E_choice'] = list(map(lambda x:(x,Staff.objects.get(id=x).get_name()),Order.objects.exclude(translator_C2E__isnull=True).values_list('translator_C2E_id',flat=True).distinct().exclude(translator_C2E__isnull=True)))
    data['choices']['status_choice'] = util.STATUS_CHOICES
    data['choices']['trans_status_choice'] = util.TRANS_STATUS_CHOICE
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
    C2E_assignee_ids = []
    C2E_assignee_names = []

    for e in Staff.objects.filter(role=1):
        C2E_assignee_ids.append(e.user_id)
        C2E_assignee_names.append( e.get_name())

    customer = Customer.objects.get(id=assignment.customer_id)
    status = util.status_dict[int(assignment.status)]
    """
    if request.method == 'POST':
        if assignment.get_status() <= util.TRANSLATING_ORIGIN:
            form = C2E_AssignForm(request.POST)
        else:
            form = E2C_AssignForm(request.POST)
        if not form.is_valid():
            return render(request, 'assign.html', {
                'form': form,
                'assignment': assignment,
                'supervisor': supervisor
            })
        else:
            translator_id = form.cleaned_data.get('assignee')
            manual_assign(assignment, Staff.objects.get(user_id=translator_id))
            return render(request, 'detail.html', {
                'assignment': assignment,
                'supervisor': supervisor,

            })
    else:
        if assignment.get_status() <= 3:
            form = C2E_AssignForm()
        else:
            form = E2C_AssignForm()
        return render(request, 'assign.html', {
            'form': form,
            'supervisor': supervisor,
            'assignment': assignment
        })
    """
    return render(request, 'assign.html', {
        'supervisor': supervisor,
        'assignment': assignment,
        'assignee_names': C2E_assignee_names,
        'assignee_ids':C2E_assignee_ids
    })


def detail(request, id, order_id):
    assignment = Order.objects.get(id=order_id)
    supervisor = Staff.objects.get(user_id=id)
    if (request.POST.get('delete')):
        assignment.delete()
        return render(request, 'supervisor_order_status.html', {
            'status': 'All',
            'supervisor': supervisor,
        })

    return render(request, 'detail.html', {
        'assignment': assignment,
        'supervisor': supervisor,
    })


@login_required
def approve(request, id, order_id):
    assignment = Order.objects.get(id=order_id)
    supervisor = Staff.objects.get(user_id=id)
    trans_C2E = assignment.translator_C2E
    trans_E2C = assignment.translator_E2C
    customer = Customer.objects.get(id=assignment.customer_id)
    status = util.status_dict[int(assignment.status)]
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
                    assignment.change_status(util.DONE)  # TODO: Customer check order complete function
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
                'trans_E2C': trans_E2C

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
    if (request.POST.get('delete')):
        document = Document.objects.get(document=request.POST.get('document'))
        document.delete()
        return render(request, 'manage_files.html', {
            'supervisor': supervisor,
            'assignment': assignment
        })
    if request.method == 'POST' and request.FILES['feedback_files']:
        file = request.FILES['feedback_files']
        fs = FileSystemStorage()
        filename = fs.save(file.name, file)
        document = Document(order=assignment, document=file, is_translated = False, type = 2) #create feedback file
        document.save()
        if not assignment.auto_assigned:
            assignment.change_status(util.RETURN)
            auto_assign(assignment)
        assignment.save()
        return render(request, 'manage_files.html', {
            'supervisor': supervisor,
            'assignment': assignment
        })
    else:

        return render(request, 'manage_files.html', {
            'supervisor': supervisor,
            'assignment': assignment
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

def create_questionnaire(request):

    #TODO: Add error message and output pdf.
    msg = ""
    data = request.GET.get('data',None)
    hospital_id = request.GET.get('hospital',None)
    disease_id = request.GET.get('disease',None)
    category = request.GET.get('category',None)
    q = Questionnaire.objects.get_or_create(hospital_id=hospital_id, disease_id=disease_id,category=category)[0]
    t = loader.get_template('question_format.txt')
    json_acceptable_string = data.replace("'", "\"")
    data = json.loads(json_acceptable_string)
    data_list = []
    for each in data:
        tuple_= ("Question Number: ",each,"Question: ",data[each]["question"],"Question Format: ",data[each]["format"],"Choices: ",)
        #tuple_+= tuple(data[each]["choices"])
        data_list.append(tuple(map(lambda k: str(k), tuple_)))
        data_list.append((map(lambda k: str(k),data[each]["choices"])))
    c = {
        'data': data_list,
    }
    myFile = default_storage.save(util.questions_path(q, 'questions.txt'), ContentFile(t.render(c)))
    q.questions = myFile
    #assignee = Staff.objects.filter(role=2).order_by('sequence')[0]
    #q.translator = assignee
    q.save()
    response = StreamingHttpResponse(myFile)
    response['Content-Disposition'] = 'attachment; filename="questions.txt"'  # download no need to change
    return response

def generate_questionnaire(request,hospital_id,disease_id):
    supervisor = Staff.objects.get(user = request.user)
    question_form = GenerateQuestionnaireForm()
    choice_form = ChoiceForm()
    return render(request, 'generate_questionnaire.html', {
        'question_form': question_form,
        'choice_form':choice_form,
        'supervisor':supervisor,
        'hospital':hospital_id,
        'disease':disease_id,
        'category':'unknown'
    })

def render_questionnaire(request,questionnaire_id):
    q = Questionnaire.objects.get(id = - questionnaire_id)
    template = q.questions
    content = default_storage.open(template).read()
    return render(request,'render_questionnaire.html'),{
        'questionnaire_id':questionnaire_id
    }