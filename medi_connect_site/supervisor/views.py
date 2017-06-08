# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from translator.models import Translator
from supervisor.models import Supervisor
from helper.models import Document,Order
from supervisor.forms import TransSignUpForm, AssignForm, ApproveForm
# Create your views here.
@login_required
def supervisor(request,user):
	#supervisor = Supervisor.objects.get(user = user)
	documents = Document.objects.all()
	translators = Translator.objects.all()
	return render(request, 'supervisor_home.html',{
		'documents': documents,
		'translators': translators
		})

@login_required
def assign(request):
	if request.method == 'POST':
		form = AssignForm(request.POST)
		if not form.is_valid():
			return render(request, 'assign.html',
							{'form':form})
		else:
			document = form.cleaned_data.get('document')
			trnaslator = form.cleaned_data.get('translator')
	else:
		return render(request,'assign.html',
						{'form': AssignForm()})

@login_required
def approve(request):
	if request.method == 'POST':
		form = ApproveForm(request.POST)
		if not form.is_valid():
			return render(request, 'approve.html',
							{'form':form})
		else:
			document = form.cleaned_data.get('document')
			approval = form.cleaned_data.get('approval')
	else:
		return render(request,'approve.html',
						{'form': ApproveForm()})

@login_required
def trans_signup(request):
    if request.method == 'POST':
        form = TransSignUpForm(request.POST)
        if not form.is_valid():
            return render(request, 'trans_signup.html',
                          {'form': form})
        else:
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            User.objects.create_user(username=username, password=password,
                                     email=email, first_name=first_name, last_name=last_name,is_staff = True)
            user = authenticate(username=username, password=password)
            login(request, user)
            translator = Translator(user=user)
            translator.save()
            return redirect('/translator/login')

    else:
        return render(request, 'trans_signup.html',
                      {'form': TransSignUpForm()})
