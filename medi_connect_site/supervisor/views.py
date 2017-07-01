# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.views.generic.edit import FormView
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from customer.models import Customer
from django.apps import apps
from supervisor.models import Supervisor
from translator.models import Translator
from supervisor.forms import TransSignUpForm,DetailForm,ResetPasswordForm,FeedbackUploadForm

Order = apps.get_model('helper','Order')
Document = apps.get_model('helper','Document')
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



# Translator Sequence Chinese to English
trans_list_C2E = list(User.objects.filter(is_staff = 1).values('id'))

# Translator Sequence English to Chinese
trans_list_E2C = list(User.objects.filter(is_staff = 1).values('id'))

# Function to move the position of a translator in sequence
def move(trans_list, translator_id, new_position):
    old_position = trans_list.index(translator_id)
    trans_list.insert(new_position, trans_list.pop(old_position))
    return trans_list


# New assign function: take out the parameter, check status in method and return translator id
def assign(self):
	is_C2E = True if self.status <= 3 else False
	if is_C2E:
		translator_id = (id for id in trans_list_C2E if len(User.objects.filter(id=id)) != 0)
		move(trans_list_C2E, translator_id, -1)
		translator = User.objects.get(id=translator_id)
		self.translator_C2E = translator
		self.change_status(TRANSLATING_ORIGIN)
	else:
		translator_id = (id for id in trans_list_E2C if len(User.objects.filter(id=id)) != 0)
		move(trans_list_E2C, translator_id, -1)
		translator = User.objects.get(id=translator_id)
		self.translator_E2C = translator
		self.change_status(TRANSLATING_FEEDBACK)


# manually assign order to a translator
def assign_manually(self, translator):
	is_C2E = True if self.status <= 3 else False
	if is_C2E:
		self.translator_C2E = translator
		self.change_status(TRANSLATING_ORIGIN)
	else:
		self.translator_E2C = translator
		self.change_status(TRANSLATING_FEEDBACK)
@login_required
def supervisor(request,id):
	supervisor = User.objects.get(id = id)
	orders = Order.objects.all()
	translators = User.objects.filter(is_staff = 1)
	customers = Customer.objects.all()
	return render(request, 'supervisor_home.html',{
		'orders': orders,
		'translators': translators,
		'customers': customers,
		'supervisor': supervisor,

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
def detail(request,id,order_id):
	assignment = Order.objects.get(id = order_id)
	supervisor = User.objects.get(id = id)
	translaotr = assignment.translator_C2E if assignment.get_status() <=3 else assignment.translator_E2C
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

