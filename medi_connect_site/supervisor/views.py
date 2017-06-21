# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from customer.models import Customer
from translator.models import Translator
from supervisor.models import Supervisor
from helper.models import Document,Order, trans_list_1, trans_list_2
from supervisor.forms import TransSignUpForm,DetailForm,ResetPasswordForm
import random
# Create your views here.


@login_required
def supervisor(request,user):
	supervisor = Supervisor.objects.get(user = user)
	orders = Order.objects.all()
	translators = Translator.objects.all()
	customers = Customer.objects.all()
	return render(request, 'supervisor_home.html',{
		'orders': orders,
		'translators': translators,
		'customers': customers,
		'supervisor': supervisor,

		})

@login_required
def trans_signup(request,user):
    supervisor = Supervisor.objects.get(user = user)
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
def detail(request,user,assignment):
	supervisor = Supervisor.objects.get(user = user)
	translator = Translator.objects.get(id = assignment.translator)
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
					assignment.translator_1 = translator_id
				else:
					assignment.translator_2 = translator_id

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
					for document in assignment.pending:
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
				assignment.translator_2 = assignment.assign(trans_list_2)
				files = request.FILES['document']
				for f in files:
					instance = Document(document = f, is_origin = True)
					instance.save()
					#assignment.pending.add(instance)
					assignment.feedback.add(instance)
		else:
			return render(request,'detail.html',{
				'form':DetailForm(),
				'supervisor':supervisor,
				'assignment':assignment
			})

@login_required
def customer_list(request,user):
	supervisor = Supervisor.objects.get(user = user )
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
		return render(request,'customer_list',{
			'customers':customers
		})



