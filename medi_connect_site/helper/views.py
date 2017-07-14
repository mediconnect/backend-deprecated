from django.shortcuts import render, redirect
from models import Hospital, Patient, Disease, Order, Document, Staff
from customer.models import Customer
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from helper.forms import OrderFormFirst, OrderFormSecond, DocumentForm
from django.utils.http import urlquote
from django.core.files.storage import FileSystemStorage

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


trans_list_C2E = list(Staff.objects.filter(role=1).values_list('id', flat=True))
trans_list_E2C = list(Staff.objects.filter(role=2).values_list('id', flat=True))

def move(trans_list, translator_id, new_position):
    old_position = trans_list.index(translator_id)
    trans_list.insert(new_position, trans_list.pop(old_position))
    return trans_list


def assign(order):
    is_C2E = True if order.status <= 3 else False
    print trans_list_C2E[0]
    print len(trans_list_C2E)
    if is_C2E:
        translator = Staff.objects.get(id=trans_list_C2E[0])
        # move(trans_list_C2E, translator.id, -1)
        order.translator_C2E = translator
        order.change_status(TRANSLATING_ORIGIN)
    else:
        translator = Staff.objects.get(id=trans_list_E2C[0])
        # move(trans_list_E2C, translator.id, -1)
        order.translator_E2C = translator
        order.change_status(TRANSLATING_FEEDBACK)


def assign_manually(self, translator):
    is_C2E = True if self.status <= 3 else False
    if is_C2E:
        self.translator_C2E = translator
        move(trans_list_C2E, translator.id, -1)
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


# those are helper methods for reducing too many if conditions
def slot_0(hosp):
    hosp.slots_open_0 -= 1


def slot_1(hosp):
    hosp.slots_open_1 -= 1


def slot_2(hosp):
    hosp.slots_open_2 -= 1


def slot_3(hosp):
    hosp.slots_open_3 -= 1


@login_required
def order_info_first(request, order_id, slot_num):
    customer = Customer.objects.get(user=request.user)
    order = Order.objects.get(id=order_id)
    order.customer = customer
    order.status = 0
    order.save()
    hosp = order.hospital
    slot_num = int(slot_num)
    avail_slot = {
        0: hosp.slots_open_0,
        1: hosp.slots_open_1,
        2: hosp.slots_open_2,
        3: hosp.slots_open_3,
    }[slot_num]
    if avail_slot < 1:
        return render(request, "hospital_order.html", {
            'hospital': hosp,
            'customer': customer,
            'order_id': order.id,
            'error': 'the hospital does not have available slot'
        })
    _ = {
        0: slot_0(hosp),
        1: slot_1(hosp),
        2: slot_2(hosp),
        3: slot_3(hosp),
    }[slot_num]
    hosp.save()
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
            extra_doc_comment = form.cleaned_data.get('extra_document_comment')
            extra_doc_description = form.cleaned_data.get('extra_document_description')
            for f in request.FILES.getlist('extra_document'):
                fs = FileSystemStorage()
                fs.save(f.name, f)
                extra_doc = Document(document=f, comment=extra_doc_comment,
                                     description=extra_doc_description, order=order)
                extra_doc.save()
                order.origin.add(extra_doc)
            doc_comment = form.cleaned_data.get('document_comment')
            doc_description = form.cleaned_data.get('document_description')
            for f in request.FILES.getlist('document'):
                fs = FileSystemStorage()
                fs.save(f.name, f)
                doc = Document(document=f, comment=doc_comment, description=doc_description, order=order)
                doc.save()
                order.origin.add(doc)
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
        order.save()
        assign(order)
        return render(request, 'finish.html', {
            'customer': customer,
        })
    else:
        customer = Customer.objects.get(user=request.user)
        return render(request, 'finish.html', {
            'customer': customer,
        })
