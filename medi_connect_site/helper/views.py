from django.shortcuts import render, redirect
from django.http import JsonResponse
from models import Hospital, Patient, Disease, Order, Document, Staff, LikeHospital, OrderPatient, Rank
from customer.models import Customer
from django.contrib.auth.decorators import login_required
from helper.forms import PatientInfo, AppointmentInfo
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

trans_list_C2E = list(Staff.objects.filter(role=1).values_list('id', flat=True))
trans_list_E2C = list(Staff.objects.filter(role=2).values_list('id', flat=True))


def move(trans_list, translator, new_position):
    old_position = trans_list.index(translator)
    trans_list.insert(new_position, trans_list.pop(old_position))
    return trans_list


def assign_auto(order):
    is_C2E = True if order.status <= 3 else False
    if is_C2E:
        translator = Staff.objects.filter(role = 1).order_by('?').first()
        #move(trans_list_C2E, translator.id, -1)
        order.translator_C2E = translator
        order.change_status(TRANSLATING_ORIGIN)
        order.change_trans_status(NOT_STARTED)
        order.save()
    else:
        translator = Staff.objects.filter(role=2).order_by('?').first()
        #move(trans_list_E2C, translator.id, -1)
        order.translator_E2C = translator
        order.change_status(TRANSLATING_FEEDBACK)
        order.change_trans_status(NOT_STARTED)
        order.save()


# Create your views here.
@login_required
def hospital(request, hospital_id, disease_id):
    """
    :param request:
    :param hospital_id: Hospital of the order
    :param disease_id: Disease of the order
    :return:
    this function takes two parameters to record the hospital customer chooses and
    the disease customer searches. it will create order or fetch an order from database
    if previous order is not done. it will then pass the data to front end of hospital order
    placement page.
    """
    hosp = Hospital.objects.get(id=hospital_id)
    dis = Disease.objects.get(id=disease_id)
    print dis
    customer = Customer.objects.get(user=request.user)
    order_list = Order.objects.filter(customer=customer, hospital=hosp, disease=dis)
    order = None
    for each in order_list:
        if int(each.status) == 0:
            order = each
            break
    order = Order(hospital=hosp, status=0, disease=dis, customer=customer) if order is None else order
    order.save()
    return render(request, "hospital_order.html", {
        'hospital': hosp,
        'rank': Rank.objects.get(hospital=hosp, disease=dis).rank,
        'disease': dis,
        'customer': customer,
        'order_id': order.id,
    })


@login_required
def order_info_first(request, order_id, slot_num):
    """
    :param request:
    :param order_id: Order
    :param slot_num: Hospital slot customer chooses
    :return:
    this function takes request from the hospital order placement page. the function has two jobs.
    1. check the available slot of hospital, and return error if there is not available slot.
    2. redirect to specific function according to the order status.
    """
    customer = Customer.objects.get(user=request.user)
    order = Order.objects.get(id=order_id)
    order.customer = customer
    order.status = 0
    hosp = order.hospital
    slot_num = int(slot_num)
    if order.week_number_at_submit != 0:
        if slot_num == 1:
            hosp.slots_open_0 += 1
        elif slot_num == 2:
            hosp.slots_open_1 += 1
        elif slot_num == 3:
            hosp.slots_open_2 += 1
        else:
            hosp.slots_open_3 += 1
    order.week_number_at_submit = slot_num
    order.save()
    avail_slot = {
        1: hosp.slots_open_0,
        2: hosp.slots_open_1,
        3: hosp.slots_open_2,
        4: hosp.slots_open_3,
    }[slot_num]
    if avail_slot < 1:
        return render(request, "hospital_order.html", {
            'hospital': hosp,
            'customer': customer,
            'order_id': order.id,
            'error': 'the hospital does not have available slot'
        })
    if slot_num == 1:
        hosp.slots_open_0 -= 1
    elif slot_num == 2:
        hosp.slots_open_1 -= 1
    elif slot_num == 3:
        hosp.slots_open_2 -= 1
    else:
        hosp.slots_open_3 -= 1
    hosp.save()
    return render(request, 'order_info_first.html', {
        'customer': customer,
        'form': PatientInfo(instance=request.user, initial={
            'contact': customer.get_name(),
            'email': customer.email,
            'address': customer.address,
            'zipcode': customer.zipcode,
            'name': order.patient_order.name if order.patient_order is not None else '',
            'age': order.patient_order.age if order.patient_order is not None else '',
            'gender': order.patient_order.gender if order.patient_order is not None else '',
            'relationship': order.patient_order.relationship if order.patient_order is not None else '',
            'passport': order.patient_order.passport if order.patient_order is not None else '',
        }),
        'order_id': order.id,
    })


@login_required
def order_submit_first(request, order_id):
    if request.method == 'POST':
        form = PatientInfo(request.POST)
        order = Order.objects.get(id=order_id)
        customer = Customer.objects.get(user=request.user)
        if not form.is_valid():
            return render(request, 'order_info_first.html', {
                'form': form,
                'order_id': order.id,
                'customer': customer,
            })
        else:
            name = form.cleaned_data.get('name')
            age = form.cleaned_data.get('age')
            gender = form.cleaned_data.get('gender')
            relationship = form.cleaned_data.get('relationship')
            passport = form.cleaned_data.get('passport')
            # create patient or fetch accordingly
            patient = Patient() if order.patient is None else order.patient
            patient.customer = customer
            patient.name = name
            patient.age = age
            patient.gender = gender
            patient.relationship = relationship
            patient.passport = passport
            patient.save()
            order.patient = patient

            order.status = 0

            order_patient = OrderPatient() if order.patient_order is None else order.patient_order
            order_patient.name = name
            order_patient.age = age
            order_patient.gender = gender
            order_patient.relationship = relationship
            order_patient.passport = passport
            order_patient.save()
            order.patient_order = order_patient

            order.save()
            return render(request, 'order_info_second.html', {
                'customer': customer,
                'form': AppointmentInfo(instance=customer, initial={
                    'hospital': order.hospital.name,
                    'hospital_address': order.hospital.area,
                    'time': order.submit,
                    'name': order.disease.name,
                    'diagnose_hospital': order.patient_order.diagnose_hospital if order.patient_order is not None else '',
                    'doctor': order.patient_order.doctor if order.patient_order is not None else '',
                    'contact': order.patient_order.contact if order.patient_order is not None else '',
                }),
                'order_id': order.id,
            })
    else:
        customer = Customer.objects.get(user=request.user)
        order = Order.objects.get(id=order_id)
        return render(request, 'order_info_second.html', {
            'customer': customer,
            'form': AppointmentInfo(instance=customer, initial={
                'hospital': order.hospital.name,
                'hospital_address': order.hospital.area,
                'time': order.submit,
                'name': order.disease.name,
                'diagnose_hospital': order.patient_order.diagnose_hospital if order.patient_order is not None else '',
                'doctor': order.patient_order.doctor if order.patient_order is not None else '',
                'contact': order.patient_order.contact if order.patient_order is not None else '',
            }),
            'order_id': order_id,
        })


@login_required
def order_patient_select(request, order_id):
    customer = Customer.objects.get(user=request.user)
    order = Order.objects.get(id=order_id)
    patients = Patient.objects.filter(customer=customer)
    return render(request, 'order_patient_select.html', {
        'customer': customer,
        'order_id': order.id,
        'patients': patients,
    })


@login_required
def order_patient_finish(request, order_id, patient_id):
    customer = Customer.objects.get(user=request.user)
    order = Order.objects.get(id=order_id)
    patient = Patient.objects.get(id=patient_id)
    order.patient = patient
    order_patient = OrderPatient(name=patient.name, age=patient.age, gender=patient.gender,
                                 relationship=patient.relationship, passport=patient.passport, contact=patient.contact)
    order_patient.save()
    order.patient_order = order_patient
    order.save()
    return render(request, 'order_info_second.html', {
        'customer': customer,
        'form': AppointmentInfo(instance=customer, initial={
            'hospital': order.hospital.name,
            'hospital_address': order.hospital.area,
            'time': order.submit,
            'name': order.disease.name,
            'diagnose_hospital': order.patient_order.diagnose_hospital if order.patient_order is not None else '',
            'doctor': order.patient_order.doctor if order.patient_order is not None else '',
            'contact': order.patient_order.contact if order.patient_order is not None else '',
        }),
        'order_id': order.id,
    })


@login_required
def order_submit_second(request, order_id):
    order = Order.objects.get(id=order_id)
    customer = Customer.objects.get(user=request.user)
    if request.method == 'POST':
        form = AppointmentInfo(request.POST, request.FILES, instance=customer)
        if not form.is_valid():
            return render(request, 'order_info_second.html', {
                'form': form,
                'order_id': order.id,
                'customer': customer,
            })
        else:
            doc_description = form.cleaned_data.get('document_description')
            for f in request.FILES.getlist('document'):
                fs = FileSystemStorage()
                fs.save(f.name, f)
                doc = Document(document=f, description=doc_description, order=order)
                doc.save()
                order.origin.add(doc)
            doctor = form.cleaned_data.get('doctor')
            hospital = form.cleaned_data.get('diagnose_hospital')
            contact = form.cleaned_data.get('contact')
            patient = order.patient_order
            patient.doctor = doctor
            patient.diagnose_hospital = hospital
            patient.contact = contact
            patient.save()
            order.save()
            return render(request, 'order_review.html', {
                'customer': customer,
                'order': order,
            })
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
        assign_auto(order)
        return render(request, 'finish.html', {
            'customer': customer,
        })
    return render(request, 'finish.html', {
        'customer': customer,
    })


@login_required
def like_hospital(request):
    customer = Customer.objects.get(user=request.user)
    hospital_id = int(request.GET.get('hospital_id', None))
    disease_id = int(request.GET.get('disease_id', None))
    mark = True if request.GET.get('mark', 'false') == 'true' else False
    hosp = Hospital.objects.get(id=hospital_id)
    dis = Disease.objects.get(id=disease_id)
    data = LikeHospital.objects.filter(customer=customer, hospital=hosp, disease=dis)

    if not mark:
        return JsonResponse({'status': "liked"}) if len(data) > 0 else JsonResponse({'status': 'no'})

    if len(data) > 0:
        for item in data:
            item.delete()
        return JsonResponse({'status': 'no'})

    add = LikeHospital(customer=customer, hospital=hosp, disease=dis)
    add.save()
    return JsonResponse({'status': 'liked'})
