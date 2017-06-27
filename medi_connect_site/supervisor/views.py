# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.views.generic.edit import FormView
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from customer.models import Customer
from translator.models import Translator
from supervisor.models import Supervisor
from helper.models import Document,Order, trans_list_C2E, trans_list_E2C
from supervisor.forms import TransSignUpForm,DetailForm,ResetPasswordForm,FeedbackUploadForm
import random
# Create your views here.

# Translator Sequence Chinese to English
trans_list_C2E = random.shuffle(list(Translator.objects.all()))

# Translator Sequence English to Chinese
trans_list_E2C = random.shuffle(list(Translator.objects.all()))
@login_required
def supervisor(request,id):
	supervisor = User.objects.get(id = id)
	orders = Order.objects.all()
	translators = Translator.objects.all()
	customers = Customer.objects.all()
	return render(request, 'supervisor_home.html',{
		'orders': orders,
		'translators': translators,
		'customers': customers,
		'supervisor': supervisor,

		})
"""
@login_required
def supervisor(request,id):
	supervisor = Supervisor.objects.get(id = id)
	orders = Order.objects.all()
	translators = Translator.objects.all()
	customers = Customer.objects.all()
	return render(request, 'supervisor_home.html',{
		'orders': orders,
		'translators': translators,
		'customers': customers,
		'supervisor': supervisor,

		})
"""
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
            translator = Translator(user=user)
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
def detail(request,id,order_id):
	assignment = Order.objects.get(id = order_id)
	supervisor = User.objects.get(id = id)
	C2E_translator = User.objects.get(id = 11)
	E2C_translator = User.objects.get(id = 11)
	translator = C2E_translator if assignment.get_status() <=3 else E2C_translator
	if request.method == 'POST':
		form = DetailForm(request.POST)
		if 'assign' in request.POST:
			if not form.is_valid():
				return render(request, 'detail.html', {
					'form':form,
					'assignment':assignment,
					'supervisor':supervisor
				})
			else:
				translator_id = form.cleaned_data.get('new_assignee')
				assignment.assign(translator_id)
				if assignment.get_status() <= 3: #can reassign to a new translator before submitted to hospital
					assignment.translator_C2E = translator_id
				else:
					assignment.translator_E2C = translator_id

		if 'approve' in request.POST:
			if not form.is_valid():
				return render(request, 'detail.html', {
					'form': form,
					'assignment': assignment,
					'supervisor': supervisor
				})
			else:
				approval = form.cleaned_data.get('approval')
				if approval :
					if assignment.status == 2:
						assignment.change_status(3)
						translator.change_trans_status(assignment,5)
						for document in assignment.pending.all():
							assignment.origin.add(document)
					if assignment.status == 5:
						assignment.change_status(6)
						translator.change_trans_status(assignment,5)
						for document in assignment.pending.all():
							assignment.feedback.add(document)
					assignment.pending.clear()
				if not approval:
					assignment.change_status(4)
					translator.change_trans_status(assignment,1)
					for document in assignment.pending.all():
						if document.is_origin:
							assignment.origin.add(document)
						if document.is_feedback:
							assignment.feedback.add(document)

		if 'upload' in request.POST: #upload feedback documents from hospital
			if not form.is_valid():
				return render(request, 'detail.html', {
					'form': form,
					'assignment': assignment,
					'supervisor': supervisor
				})
			else:
				assignment.assign()
				files = request.FILES['feedback_files']
				for f in files:
					instance = Document(document = f, is_origin = True)
					instance.save()
					#assignment.pending.add(instance)
					assignment.feedback.add(instance)
		orders = Order.objects.all()
		translators = Translator.objects.all()
		customers = Customer.objects.all()
		return render(request, 'supervisor_home.html', {
			'orders': orders,
			'translators': translators,
			'customers': customers,
			'supervisor': supervisor,

		})

	else:
		return render(request,'detail.html',{
			'form':DetailForm(),
			'supervisor':supervisor,
			'assignment':assignment
		})

@login_required
def feedback_upload(request,id,order_id):
	assignment = Order.objects.get(id = order_id)
	supervisor = User.objects.get(id = id)
	if request.method == 'POST':
		form = FeedbackUploadForm(request.POST,request.FILES)
		if not form.is_valid():
			return render(request,'feedback_upload.html',{
				'assignment':assignment,
				'supervisor':supervisor
			})
		else:
			assignment.assign()
			files = request.FILES['feedback_files']
			for f in files:
				instance = Document(document=f, is_origin=True)
				instance.save()
				# assignment.pending.add(instance)
				assignment.feedback.add(instance)
	else:
		return render(request, 'feedback_upload.html', {
			'assignment': assignment,
			'supervisor': supervisor
		})

class FileFieldView(FormView):
    form_class = FeedbackUploadForm
    template_name = 'feedback_upload.html'  # Replace with your template.
    success_url = 'supervisor_home'  # Replace with your URL or reverse().

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        files = request.FILES.getlist('file_field')
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

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

