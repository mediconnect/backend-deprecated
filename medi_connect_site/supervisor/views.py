# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.encoding import uri_to_iri
from django.views.generic.edit import FormView
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from customer.models import Customer
from django.apps import apps
from supervisor.models import Supervisor
from translator.models import Translator_C2E, Translator_E2C
from supervisor.forms import TransSignUpForm,AssignForm,ApproveForm
from helper.models import trans_list_C2E, trans_list_E2C

Order = apps.get_model('helper','Order')
Document = apps.get_model('helper','Document')
Hospital = apps.get_model('helper','Hospital')
# Create your views here.
# Status
STARTED = 0
SUBMITTED = 1  # deposit paid, only change appointment at this status
TRANSLATING_ORIGIN = 2  # translator starts translating origin documents
RECEIVED = 3  # origin documents translated, approved and submitted to hospitals
# ============ Above is C2E status =============#
# ============Below is E2C status ==============#
RETURN = 4  # hospital returns feedback
TRANSLATING_FEEDBACK = 5  # translator starts translating feedback documents
FEEDBACK = 6  # feedback documents translated, approved, and feedback to customer
PAID = 7  # remaining amount paid

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
status_dict = ['STARTED','SUBMITTED','TRANSLATING_ORIGIN','RECEIVED','RETURN','TRANSLATING_FEEDBACK','FEEDBACK','PAID']


def move(trans_list,translator_id,new_position):
    old_position = trans_list.index(int(translator_id))
    trans_list.insert(new_position, trans_list.pop(old_position))
    return trans_list


def assign_auto(order):
    is_C2E = True if order.status <= 3 else False
    if is_C2E:
        while User.objects.filter(id = trans_list_C2E[0]).count() == 0:
            trans_list_C2E.pop()
        translator = Translator_C2E.objects.filter(id=trans_list_C2E[0])
        move(trans_list_C2E, translator.id, -1)
        order.translator_C2E = translator
        order.change_status(TRANSLATING_ORIGIN)
    else:
        while User.objects.filter(id = trans_list_E2C[0]).count() == 0:
            trans_list_C2E.pop()
        translator = Translator_E2C.objects.filter(id=trans_list_E2C[0])
        move(trans_list_E2C, translator.id, -1)
        order.translator_E2C = translator
        order.change_status(TRANSLATING_FEEDBACK)
	order.save()

def assign_manually(order, translator):
    is_C2E = True if order.status <= 3 else False
    if is_C2E:
        order.translator_C2E = translator
        move(trans_list_C2E,translator.id,-1)
        order.change_status(TRANSLATING_ORIGIN)
    else:
        order.translator_E2C = translator
        move(trans_list_C2E, translator.id, -1)
        order.change_status(TRANSLATING_FEEDBACK)
	order.save()


@login_required
def supervisor(request,id):
	supervisor = Supervisor.objects.get(id = id)
	orders = Order.objects.all()
	translators_E2C = Translator_E2C.objects.filter(is_staff = 1)
	translators_C2E = Translator_C2E.objects.filter(is_staff = 1)
	customers = Customer.objects.all()
	hospitals = Hospital.objects.all()
	if (request.POST.get('hospital_btn')):
		hospital = Hospital.objects.get(name = request.POST.get('hospital'))
		hospital.reset_slot()
	return render(request, 'supervisor_home.html',{
		'orders': orders,
		'translators_E2C': translators_E2C,
		'translators_C2E':translators_C2E,
		'customers': customers,
		'supervisor': supervisor,
		'hospitals': hospitals,

		})

@login_required
def trans_signup(request,id):
    supervisor = User.objects.get(id = id)
    if request.method == 'POST':
        form = TransSignUpForm(request.POST)
        if not form.is_valid():
            return render(request,'trans_signup.html',
                          {'form':form,
                           'supervisor':supervisor
                          })
        else:
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password')
            user = authenticate(username=username,password = raw_password,is_staff = True)
            translator = User(user=user)
            return render(request,'trans_signup.html',
						  {	'form':form,
							'supervisor':supervisor
            })
    else:
        return render(request,'trans_signup.html',
                      {'form':TransSignUpForm(),
                       'supervisor':supervisor}
                      )

@login_required
def assign(request,id,order_id):
	assignment = Order.objects.get(id = order_id)
	supervisor = User.objects.get(id = id)
	customer = Customer.objects.get(id=assignment.customer_id)
	status = status_dict[int(assignment.status)]
	if request.method == 'POST':
		form = AssignForm(request.POST)
		if not form.is_valid():
			return render(request,'assign.html',{
				'form':form,
				'assignment':assignment,
				'supervisor':supervisor
			})
		else:
			translator_id = form.cleaned_data.get('new_assignee')
			if assignment.get_status() <= 3:
				assign_manually(assignment,Translator_C2E.objects.get(id = translator_id))
			else:
				assign_manually(assignment, Translator_C2E.objects.get(id=translator_id))
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
def detail(request,id,order_id):
	assignment = Order.objects.get(id=order_id)
	supervisor = User.objects.get(id=id)
	customer = Customer.objects.get(id = assignment.customer_id)
	status = status_dict[int(assignment.status)]
	trans_C2E =  assignment.translator_C2E.get_name()
	trans_E2C = assignment.translator_E2C.get_name()
	return render(request, 'detail.html', {
		'assignment': assignment,
		'supervisor': supervisor,
		'status':status,
		'customer':customer,
		'trans_C2E':trans_C2E,
		'trans_E2C':trans_E2C

	})

@login_required
def approve(request,id,order_id):
	assignment = Order.objects.get(id = order_id)
	supervisor = Supervisor.objects.get(id = id)
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
				if assignment.status == 2:
					assignment.change_status(3)
					for document in assignment.pending.all():
						assignment.origin.add(document)
				if assignment.status == 5:
					assignment.change_status(6)
					for document in assignment.pending.all():
						assignment.feedback.add(document)
				assignment.pending.clear()
			if not approval:
				assignment.change_status(4)
				for document in assignment.pending.all():
					if document.is_origin:
						assignment.origin.add(document)
					if document.is_feedback:
						assignment.feedback.add(document)


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
def manage_files(request,id,order_id):
	assignment = Order.objects.get(id = order_id)
	supervisor = User.objects.get(id = id)
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
		filename = fs.save(file.name,file)
		document = Document(order = assignment,document = file,is_origin = True)
		document.save()
		assignment.feedback.add(document)
		assignment.save()
		return render(request, 'manage_files.html', {
			'supervisor': supervisor,
			'assignment': assignment
		})
	else:

		return render(request,'manage_files.html',{
				'supervisor':supervisor,
				'assignment':assignment
			})

@login_required
def customer_list(request,id):
	supervisor = Supervisor.objects.get(id = id )
	customers = Customer.objects.all()
	if request.method == 'POST':
		form = ResetPasswordForm(request.POST)
		if not form.is_valid():
			return render(request,'customer_list.html'),
			{
				'form': form,
				'supervisor':supervisor,
				'customers':customers
			}
		else:
			customer = form.cleaned_data.get('customer')
			#implement reset password function
	else:
		return render(request,'customer_list.html',{
			'customers':customers
		})
