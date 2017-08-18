# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.encoding import uri_to_iri
from django.views.generic.edit import FormView
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from customer.models import Customer
from django.apps import apps
from supervisor.forms import TransSignUpForm, AssignForm, ApproveForm,PasswordResetForm
from helper.models import Staff
from django.core import serializers
from django.http import JsonResponse
from django import template
import json
import django.utils.encoding as encode


Order = apps.get_model('helper', 'Order')
Document = apps.get_model('helper', 'Document')
Hospital = apps.get_model('helper', 'Hospital')
Disease = apps.get_model('helper','Disease')
# Create your views here.
# Status
STARTED = 0
PAID = 1  # paid
RECEIVED = 2  # order received
TRANSLATING_ORIGIN = 3  # translator starts translating origin documents
SUBMITTED = 4  # origin documents translated, approved and submitted to hospitals
# ============ Above is C2E status =============#
# ============Below is E2C status ==============#
RETURN = 5  # hospital returns feedback
TRANSLATING_FEEDBACK = 6  # translator starts translating feedback documents
FEEDBACK = 7  # feedback documents translated, approved, and feedback to customer

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

status_dict = ['STARTED', 'PAID','RECEIVED', 'TRANSLATING_ORIGIN', 'SUBMITTED', 'RETURN', 'TRANSLATING_FEEDBACK', 'FEEDBACK']
# Trans_status

NOT_STARTED = 0  # assignment not started yet
ONGOING = 1  # assignment started not submitted to supervisor
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
trans_status_dict = ['NOT_STARTED','ONGOING','APPROVING','APPROVED','FINISHED']

trans_list_C2E = list(Staff.objects.filter(role=1).values_list('id', flat=True))
trans_list_E2C = list(Staff.objects.filter(role=2).values_list('id', flat=True))


def move(trans_list, translator, new_position):
    old_position = trans_list.index(translator)
    trans_list.insert(new_position, trans_list.pop(old_position))
    return trans_list


def assign_auto(order):
    is_C2E = True if order.status <= 3 else False
    if is_C2E:
        translator = Staff.objects.get(id=trans_list_C2E[0])
        move(trans_list_C2E, translator.id, -1)
        order.translator_C2E = translator
        order.change_status(TRANSLATING_ORIGIN)
    else:
        translator = Staff.objects.get(id=trans_list_E2C[0])
        move(trans_list_E2C, translator.id, -1)
        order.translator_E2C = translator
        order.change_status(TRANSLATING_FEEDBACK)
        order.save()


def assign_manually(order, translator):
    is_C2E = True if order.status <= 3 else False
    if is_C2E:
        order.translator_C2E = translator
        move(trans_list_C2E, translator, -1)
        order.change_status(TRANSLATING_ORIGIN)
    else:
        order.translator_E2C = translator
        move(trans_list_C2E, translator, -1)
        order.change_status(TRANSLATING_FEEDBACK)
        order.save()

register = template.Library()
@register.filter(name='forcetext')
def forcetext(value):
    return encode.force_text(value)

@login_required()
def update_result(request):
    field = request.GET.get('field',None)
    value = request.GET.get('value', None)
    if value != 'ALL':
        filter = field + '__' + 'exact'
        orders = Order.objects.filter(**{filter: value})
    else:
        orders = Order.objects.all()
    paginator = Paginator(orders, 2)
    page = request.GET.get('page')
    try:
        orders = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        orders = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        orders = paginator.page(paginator.num_pages)
    data={
        'results':[],
        'choices':[],
        'has_previous':orders.has_previous(),
        'has_next':orders.has_next(),
        'number':orders.number,
        'num_pages':orders.paginator.num_pages
    }
    if data['has_previous']:
        data['previous_page_number']=orders.previous_page_number()
    if data['has_next']:
        data['next_page_number']=orders.next_page_number()
    """
        previous_page_number
        next_page_number
        number
        num_pages
    """
    choices = {
        'customer_choices':[],
        'patient_choices':[],
        'hospital_choices':[],
        'disease_choices':[],
        'translator_C2E_choices':[],
        'translator_E2C_choices':[],
        'status_choices':[],
        'trans_status_choices':[]

    }
    results = []
    for each in orders:
        result={
            'Order_id':each.id,
            'Customer': (each.customer.id,each.customer.get_name()),
            'Patient': (each.patient.id,each.patient.name),
            'Hospital':(each.hospital.id,each.hospital.name),
            'Disease':(each.disease.id,each.disease.name),
            'Translator_C2E':(each.translator_C2E.id,each.translator_C2E.get_name()),
            'Translator_E2C':(each.translator_E2C.id,each.translator_C2E.get_name()),
            'Status':(each.status,each.get_status()),
            'Translator Status':(each.trans_status,each.get_trans_status()),
            'Deadline':each.get_deadline(),
            'Submit Deadline':each.get_submit_deadline()
        }
        results.append(result)
    for each in results:
        if each['Customer'] not in choices['customer_choices'] or choices['customer_choices'] is None:
            choices['customer_choices'].append(each['Customer'])
        if each['Patient'] not in choices['patient_choices'] or choices['patient_choices'] is None:
            choices['patient_choices'].append(each['Patient'])
        if each['Hospital'] not in choices['hospital_choices'] or choices['hospital_choices'] is None:
            choices['hospital_choices'].append(each['Hospital'])
        if each['Disease'] not in choices['disease_choices'] or choices['disease_choices'] is None:
            choices['disease_choices'].append(each['Disease'])
        if each['Translator_C2E'] not in choices['translator_C2E_choices']or choices['translator_C2E_choices'] is None:
            choices['translator_C2E_choices'].append(each['Translator_C2E'])
        if each['Translator_E2C'] not in choices['translator_E2C_choices']or choices['translator_E2C_choices'] is None:
            choices['translator_E2C_choices'].append(each['Translator_E2C'])
        if each['Status'] not in choices['status_choices']or choices['status_choices'] is None:
            choices['status_choices'].append(each['Status'])
        if each['Translator Status'] not in choices['trans_status_choices']or choices['trans_status_choices'] is None:
            choices['trans_status_choices'].append(each['Translator Status'])
    data['results']=results
    data['choices']=choices
    return JsonResponse(data)


@login_required
def supervisor(request, id):
    supervisor = Staff.objects.get(user_id=id)
    orders = Order.objects.all()
    paginator=Paginator(orders,25)
    page=request.GET.get('page')
    try:
        orders = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        orders = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        orders = paginator.page(paginator.num_pages)
    return render(request, 'supervisor_home.html', {
        'orders': orders,
        'supervisor': supervisor,
    })

def order_status(request, id,status):
    supervisor = Staff.objects.get(user_id=id)
    if status != 'ALL':
        orders = Order.objects.filter(trans_status = status)
    else:
        orders = Order.objects.all()
    return render(request, 'supervisor_order_status.html', {
        'status':status,
        'orders': orders,
        'supervisor': supervisor,
    })


@login_required
def trans_signup(request, id):
    supervisor = Staff.objects.get(user_id=id)
    if request.method == 'POST':
        form = TransSignUpForm(request.POST)
        if not form.is_valid():
            return render(request, 'trans_signup.html',
                          {'form': form,
                           'supervisor': supervisor
                           })
        else:
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=raw_password, is_staff=True)
            translator = User(user=user)
            return render(request, 'trans_signup.html',
                          {'form': form,
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
    supervisor = Staff.objects.get(id=id)
    customer = Customer.objects.get(id=assignment.customer_id)
    status = status_dict[int(assignment.status)]
    if request.method == 'POST':
        form = AssignForm(request.POST)
        if not form.is_valid():
            return render(request, 'assign.html', {
                'form': form,
                'assignment': assignment,
                'supervisor': supervisor
            })
        else:
            translator_id = form.cleaned_data.get('new_assignee')
            if assignment.get_status() <= 3:
                assign_manually(assignment, Staff.objects.get(id=translator_id))
            else:
                assign_manually(assignment, Staff.objects.get(id=translator_id))
            trans_C2E = assignment.translator_C2E.get_name()
            trans_E2C = assignment.translator_E2C.get_name()
            return render(request, 'detail.html', {
                'assignment': assignment,
                'supervisor': supervisor,
                'status': status,
                'customer': customer,
                'trans_C2E': trans_C2E,
                'trans_E2C': trans_E2C

            })
    else:
        form = AssignForm()
        return render(request, 'assign.html', {
            'form': form,
            'supervisor': supervisor,
            'assignment': assignment
        })


def detail(request, id, order_id):
    assignment = Order.objects.get(id=order_id)
    supervisor = Staff.objects.get(user_id=id)
    if (request.POST.get('delete')):
        assignment.delete()
        orders = Order.objects.all()
        customer_choice = list(Customer.objects.all().distinct())
        hospital_choice = list(Hospital.objects.all().distinct())
        disease_choice = list(Disease.objects.all().distinct())
        translator_C2E_choice = list(Staff.objects.filter(role=1).distinct())
        translator_E2C_choice = list(Staff.objects.filter(role=2).distinct())
        return render(request, 'supervisor_home.html', {
            'customer_choice': customer_choice,
            'hospital_choice': hospital_choice,
            'disease_choice': disease_choice,
            'translator_C2E_choice': translator_C2E_choice,
            'translator_E2C_choice': translator_E2C_choice,
            'status_choice': status_dict,
            'trans_status_choice': trans_status_dict,
            'orders': orders,
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
    status = status_dict[int(assignment.status)]
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
                if assignment.get_status() == 'TRANSLATING_ORIGIN':
                    assignment.change_status(RECEIVED)

                    for document in assignment.pending.all():
                        assignment.origin.add(document)
                if assignment.get_status() == 'TRANSLATING_FEEDBACK':
                    assignment.change_status(FEEDBACK)
                    for document in assignment.pending.all():
                        assignment.feedback.add(document)
                assignment.pending.clear()
                assignment.change_trans_status(APPROVED)
                assignment.save()
            if not approval:
                for document in assignment.pending.all():
                    if document.is_origin:
                        assignment.origin.add(document)
                    if document.is_feedback:
                        assignment.feedback.add(document)
                assignment.change_trans_status(ONGOING)
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
        document = Document.objects.get(document=request.GET.get('document'))
        document.delete()
        return render(request, 'manage_files.html', {
            'supervisor': supervisor,
            'assignment': assignment
        })
    if request.method == 'POST' and request.FILES['feedback_files']:
        file = request.FILES['feedback_files']
        fs = FileSystemStorage()
        filename = fs.save(file.name, file)
        document = Document(order=assignment, document=file, is_origin=True)
        document.save()
        assignment.feedback.add(document)
        if not assignment.auto_assigned:
            assign_auto(assignment)
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
    translators = translators_C2E.union(translators_E2C)
    return render(request, 'translator_list.html', {
        'translators_C2E': translators_C2E,
        'translators_E2C': translators_E2C,
        'supervisor': supervisor,
    })


@login_required
def hospital_list(request, id):
    supervisor = Staff.objects.get(user_id=id)
    hospitals = Hospital.objects.all()
    if (request.POST.get('hospital_btn')):
        hospital = Hospital.objects.get(name=request.POST.get('hospital'))
        hospital.reset_slot()
    return render(request, 'hospital_list.html', {
        'hospitals': hospitals,
        'supervisor': supervisor,
    })
