from django.shortcuts import render, redirect
from models import Hospital, Patient, Disease, Order, Document, trans_list_C2E,trans_list_E2C
from customer.models import Customer
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from helper.forms import OrderFormFirst, OrderFormSecond, DocumentForm
from django.utils.http import urlquote

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



def move(trans_list,translator_id,new_position):
    old_position = trans_list.index(translator_id)
    trans_list.insert(new_position, trans_list.pop(old_position))
    return trans_list


def assign(order):
    is_C2E = True if order.status <= 3 else False
    if is_C2E:
        while User.objects.filter(id = trans_list_C2E[0]).count() == 0:
            trans_list_C2E.pop()
        translator = User.objects.filter(id=trans_list_C2E[0])
        move(trans_list_C2E, translator.id, -1)
        order.translator_C2E = translator
        order.change_status(TRANSLATING_ORIGIN)
    else:
        while User.objects.filter(id = trans_list_E2C[0]).count() == 0:
            trans_list_C2E.pop()
        translator = User.objects.filter(id=trans_list_E2C[0])
        move(trans_list_E2C, translator.id, -1)
        order.translator_E2C = translator
        order.change_status(TRANSLATING_FEEDBACK)

def assign_manually(self, translator):
    is_C2E = True if self.status <= 3 else False
    if is_C2E:
        self.translator_C2E = translator
        move(trans_list_C2E,translator.id,-1)
        self.change_status(TRANSLATING_ORIGIN)
    else:
        self.translator_E2C = translator
        move(trans_list_C2E, translator.id, -1)
        self.change_status(TRANSLATING_FEEDBACK)

# Create your views here.
@login_required
def hospital(request, hospital_id, disease_id):
    hosp = Hospital.objects.get(id=hospital_id)
    dis = Disease.objects.get(id=disease_id)
    customer = Customer.objects.get(user=request.user)
    order_list = Order.objects.filter(customer=customer)
    order = None
    for each in order_list:
        if hosp == each.hospital and each.status == str(0):
            order = each
    order = Order(hospital=hosp, status=0, disease=dis) if order is None else order
    order.save()
    return render(request, "hospital_order.html", {
        'hospital': hosp,
        'customer': customer,
        'order_id': order.id,
    })


@login_required
def order_info_first(request, order_id):
    customer = Customer.objects.get(user=request.user)
    order = Order.objects.get(id=order_id)
    if order.hospital.slots_open < 1:
        return render(request, "hospital_order.html", {
            'hospital': order.hospital,
            'customer': customer,
            'order_id': order.id,
            'error': "There is no available spot"
        })
    order.customer = customer
    order.status = 0
    order.save()
    if order.patient is None or order.patient.name is None or len(order.patient.name) == 0:
        return render(request, 'order_info_first.html', {
            'customer': customer,
            'form': OrderFormFirst(instance=request.user, initial={
                'diagnose_hospital': order.hospital.name
            }),
            'order_id': order.id,
        })
    else:
        return redirect('order_submit_first', order_id=order_id)


@login_required
def order_submit_first(request, order_id):
    if request.method == 'POST':
        form = OrderFormFirst(request.POST)
        order = Order.objects.get(id=order_id)
        customer = Customer.objects.get(user=request.user)
        if not form.is_valid():
            form.fields['diagnose_hospital'] = order.hospital.name
            return render(request, 'order_info_first.html', {
                'form': form,
                'order_id': order.id,
                'customer': customer,
            })
        else:
            name = form.cleaned_data.get('name')
            age = form.cleaned_data.get('age')
            gender = form.cleaned_data.get('gender')
            patient = Patient(name=name, age=age, gender=gender, customer=customer)
            patient.save()
            order.patient = patient
            order.status = 0
            order.save()
            return render(request, 'order_info_second.html', {
                'customer': customer,
                'form': OrderFormSecond(instance=request.user, initial={
                    'name': order.disease.name
                }),
                'order_id': order.id,
            })
    else:
        customer = Customer.objects.get(user=request.user)
        order = Order.objects.get(id=order_id)
        return render(request, 'order_info_second.html', {
            'customer': customer,
            'form': OrderFormSecond(instance=request.user, initial={
                'name': order.disease.name
            }),
            'order_id': order_id,
        })


@login_required
def order_submit_second(request, order_id):
    if request.method == 'POST':
        form = OrderFormSecond(request.POST)
        order = Order.objects.get(id=order_id)
        customer = Customer.objects.get(user=request.user)
        if not form.is_valid():
            form.fields['name'] = order.disease.name
            return render(request, 'order_info_second.html', {
                'form': form,
                'order_id': order.id,
                'customer': customer,
            })
        else:
            return render(request, 'document_submit.html', {
                'customer': customer,
                'form': DocumentForm(),
                'order_id': order_id,
            })
    else:
        customer = Customer.objects.get(user=request.user)
        return render(request, 'document_submit.html', {
            'customer': customer,
            'form': DocumentForm(),
            'order_id': order_id,
        })


@login_required
def document_submit(request, order_id):
    order = Order.objects.get(id=order_id)
    customer = Customer.objects.get(user=request.user)
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES, instance=customer)
        if not form.is_valid():
            return render(request, 'document_submit.html', {
                'form': form,
                'order_id': order.id,
                'customer': customer,
            })
        else:
            document = urlquote(form.cleaned_data.get('document'))
            extra_document = form.cleaned_data.get('extra_document')
            if extra_document is not None:
                extra_doc_comment = form.cleaned_data.get('extra_document_comment')
                extra_doc_description = form.cleaned_data.get('extra_document_description')
                extra_doc = Document(document=urlquote(extra_document), comment=extra_doc_comment,
                                     description=extra_doc_description, order=order)
                extra_doc.save()
                order.origin.add(extra_doc)
            doc_comment = form.cleaned_data.get('document_comment')
            doc_description = form.cleaned_data.get('document_description')
            doc = Document(document=document, comment=doc_comment, description=doc_description, order=order)
            doc.save()
            order.origin.add(doc)
            hosp = order.hospital
            hosp.slots_open -= 1
            hosp.save()
            order.save()
            return render(request, 'order_review.html', {
                'customer': customer,
                'order': order,
            })
    else:
        customer = Customer.objects.get(user=request.user)
        return render(request, 'order_review.html', {
            'customer': customer,
            'order': order,
        })


@login_required
def finish(request, order_id):
    order = Order.objects.get(id=order_id)
    customer = Customer.objects.get(user=request.user)
    if request.method == 'POST':
        order.status = 1
        order.assign()
        order.save()
        return render(request, 'finish.html', {
            'customer': customer,
        })
    else:
        customer = Customer.objects.get(user=request.user)
        return render(request, 'finish.html', {
            'customer': customer,
        })
