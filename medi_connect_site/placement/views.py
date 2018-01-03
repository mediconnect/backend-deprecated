from django.shortcuts import render, redirect
from django.http import JsonResponse
from helper.models import Hospital, Patient, Disease, Order, Document, HospitalReview, LikeHospital, OrderPatient, Rank, \
    Slot
from customer.models import Customer
from django.contrib.auth.decorators import login_required
from helper.forms import PatientInfo, AppointmentInfo
from helper.models import auto_assign
from dynamic_form.forms import create_form, get_fields, modify_form
from django.core.paginator import Paginator, EmptyPage
from django.views.generic.base import TemplateView
from django.core.files.uploadedfile import SimpleUploadedFile
import datetime
import calendar
from time import sleep
from threading import Thread
import pytz
from util import delete_order


def hospital_detail(request):
    if request.method == 'GET' and request.session.get('order_status_request', None) != 'POST':
        hospital_id = request.GET.get('hospital_id', None)
        hospital_id = request.session.get('hospital_id', None) if hospital_id is None else hospital_id
        disease_id = request.session.get('disease_id', None)
        request.session['hospital_id'] = hospital_id
        request.session['order_status'] = 'view'

        if not request.user.is_authenticated:
            return redirect('auth')

        hosp = Hospital.objects.get(id=hospital_id)
        dis = Disease.objects.get(id=disease_id)
        customer = Customer.objects.get(user=request.user)
        slot = Slot.objects.get(hospital=hosp, disease=dis)
        slots = {0: slot.slots_open_0, 1: slot.slots_open_1, 2: slot.slots_open_2, 3: slot.slots_open_3}
        comments = HospitalReview.objects.filter(hospital=hosp)
        pages = Paginator(comments, 2)
        try:
            comments = pages.page(1)
        except EmptyPage:
            comments = False
        return render(request, "hospital_detail.html", {
            'hospital': hosp,
            'rank': Rank.objects.get(disease=dis, hospital=hosp).rank,
            'slots': slots,
            'disease': dis,
            'customer': customer,
            'comments': comments,
            'duplicate': 0,
        })
    else:
        hospital_id = request.POST.get('hospital_id', None)
        slot_num = request.POST.get('slot', None)
        hospital_id = request.session.get('hospital_id', None) if hospital_id is None else hospital_id
        slot_num = request.session.get('slot_num', None) if slot_num is None else slot_num
        slot_num = int(slot_num)
        disease_id = request.session.get('disease_id', None)
        request.session['hospital_id'] = hospital_id
        request.session['slot_num'] = slot_num
        request.session['order_status'] = 'placement'
        delete = request.POST.get('delete', None)

        if not request.user.is_authenticated:
            return redirect('auth')

        hosp = Hospital.objects.get(id=hospital_id)
        dis = Disease.objects.get(id=disease_id)
        customer = Customer.objects.get(user=request.user)
        order = None
        try:
            order = Order.objects.get(customer=customer, status__lte=0)
            if delete is None:
                return render(request, "hospital_detail.html", {
                    'choose_hospital': hospital_id,
                    'choose_disease': disease_id,
                    'choose_slot': slot_num,
                    'order': order,
                    'duplicate': 1,
                    'disease': dis,
                    'hospital': hosp,
                })
            elif delete == 'delete':
                delete_order(order.id)
                order = None
        except Order.DoesNotExist:
            pass
        slot = Slot.objects.get(disease=dis, hospital=hosp)
        avail_slot = {
            0: slot.slots_open_0,
            1: slot.slots_open_1,
            2: slot.slots_open_2,
            3: slot.slots_open_3,
        }[slot_num]
        if avail_slot < 1 and not (avail_slot >= 0 and order.week_number_at_submit == slot_num):
            slot = Slot.objects.get(hospital=hosp, disease=dis)
            slots = {0: slot.slots_open_0, 1: slot.slots_open_1, 2: slot.slots_open_2, 3: slot.slots_open_3}
            comments = HospitalReview.objects.filter(hospital=hosp)
            pages = Paginator(comments, 2)
            try:
                comments = pages.page(1)
            except EmptyPage:
                comments = False

            return render(request, "hospital_detail.html", {
                'hospital': hosp,
                'rank': Rank.objects.get(disease=dis, hospital=hosp).rank,
                'slots': slots,
                'disease': dis,
                'customer': customer,
                'comments': comments,
                'error': 'the hospital does not have available slot',
                'duplicate': 0,
            })
        order = Order(hospital=hosp, status=0, disease=dis, customer=customer) if order is None else order
        order.save()
        # start thread for 5 minutes order cleaning
        Thread(target=clean_order, args=(order.id,)).start()
        # check if order chosen slot before
        if order.week_number_at_submit != -1:
            if slot_num == 0:
                slot.slots_open_0 += 1
            elif slot_num == 1:
                slot.slots_open_1 += 1
            elif slot_num == 2:
                slot.slots_open_2 += 1
            else:
                slot.slots_open_3 += 1
        order.week_number_at_submit = slot_num
        order.save()
        if slot_num == 0:
            slot.slots_open_0 -= 1
        elif slot_num == 1:
            slot.slots_open_1 -= 1
        elif slot_num == 2:
            slot.slots_open_2 -= 1
        else:
            slot.slots_open_3 -= 1
        slot.save()
        request.session['order_id'] = order.id
        return redirect('order_patient_info')


def clean_order(order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return
    while True:
        if int(order.status) >= 1:
            break
        naive = order.submit
        diff = datetime.datetime.now(tz=pytz.utc) - naive
        if diff.total_seconds() > 300:
            delete_order(order.id)
            break
        sleep(60)


@login_required
def get_comment(request):
    hospital_id = int(request.GET.get('hospital_id', None))
    page = int(request.GET.get('page', None))
    hosp = Hospital.objects.get(id=hospital_id)
    comments = HospitalReview.objects.filter(hospital=hosp)
    pages = Paginator(comments, 2)

    try:
        comments = pages.page(page + 1)
    except EmptyPage:
        comments = None

    if comments is None:
        return JsonResponse({'status': 'empty'})

    data = dict()
    data['comments'] = [x.comment for x in comments]
    data['status'] = 'exist'
    return JsonResponse(data)


@login_required
def order_patient_info(request):
    order_id = request.session['order_id']
    order_expire(order_id)
    if request.method == 'GET':
        customer = Customer.objects.get(user=request.user)
        order = Order.objects.get(id=order_id)
        pin_yin = order.patient_order.pin_yin.split() if order.patient_order is not None and len(
            order.patient_order.pin_yin) >= 3 else ['', '']
        return render(request, 'order_patient_info.html', {
            'customer': customer,
            'form': PatientInfo(instance=request.user, initial={
                'contact': customer.get_name(),
                'email': customer.user.email,
                'address': customer.address,
                'telephone': customer.tel,
                'wechat': customer.wechat if len(customer.wechat) >= 1 else 'unknown',
                'qq': customer.qq if len(customer.qq) >= 1 else 'unknown',
                'first_name': order.patient_order.first_name if order.patient_order is not None else '',
                'last_name': order.patient_order.last_name if order.patient_order is not None else '',
                'birth': order.patient_order.birth if order.patient_order is not None else '',
                'gender': order.patient_order.gender if order.patient_order is not None else '',
                'relationship': order.patient_order.relationship if order.patient_order is not None else '',
                'passport': order.patient_order.passport if order.patient_order is not None else '',
                'first_name_pin_yin': pin_yin[0],
                'last_name_pin_yin': pin_yin[1],
            }),
            'time': (datetime.datetime.now(tz=pytz.utc) - order.submit).total_seconds(),
        })
    else:
        form = PatientInfo(request.POST)
        order = Order.objects.get(id=order_id)
        customer = Customer.objects.get(user=request.user)
        if not form.is_valid():
            return render(request, 'order_patient_info.html', {
                'form': form,
                'customer': customer,
                'time': (datetime.datetime.now(tz=pytz.utc) - order.submit).total_seconds(),
            })
        first_name = form.cleaned_data.get('first_name')
        last_name = form.cleaned_data.get('last_name')
        birth = form.cleaned_data.get('birth')
        gender = form.cleaned_data.get('gender')
        relationship = form.cleaned_data.get('relationship')
        passport = form.cleaned_data.get('passport')
        first_name_pin_yin = form.cleaned_data.get('first_name_pin_yin')
        last_name_pin_yin = form.cleaned_data.get('last_name_pin_yin')
        # create patient or fetch accordingly
        patient = Patient() if order.patient is None else order.patient
        patient.customer = customer
        patient.first_name = first_name
        patient.last_name = last_name
        patient.birth = birth
        patient.gender = gender
        patient.relationship = relationship
        patient.passport = passport
        patient.pin_yin = first_name_pin_yin + ' ' + last_name_pin_yin
        patient.save()
        order.patient = patient

        order.status = -1

        order_patient = OrderPatient() if order.patient_order is None else order.patient_order
        order_patient.first_name = first_name
        order_patient.last_name = last_name
        order_patient.birth = birth
        order_patient.gender = gender
        order_patient.relationship = relationship
        order_patient.passport = passport
        order_patient.pin_yin = first_name_pin_yin + ' ' + last_name_pin_yin
        order_patient.save()
        order.patient_order = order_patient
        order.save()
        return redirect('order_document_info')


@login_required
def order_patient_select(request):
    order_id = request.session['order_id']
    order_expire(order_id)
    if request.method == 'GET':
        order_expire(order_id)
        customer = Customer.objects.get(user=request.user)
        order = Order.objects.get(id=order_id)
        patients = Patient.objects.filter(customer=customer)
        return render(request, 'order_patient_select.html', {
            'customer': customer,
            'patients': patients,
            'time': (datetime.datetime.now(tz=pytz.utc) - order.submit).total_seconds(),
        })
    else:
        patient_id = request.POST.get('patient_id')
        order_expire(order_id)
        order = Order.objects.get(id=order_id)
        patient = Patient.objects.get(id=patient_id)
        order.patient = patient
        order_patient = OrderPatient(first_name=patient.first_name, last_name=patient.last_name, birth=patient.birth,
                                     gender=patient.gender, relationship=patient.relationship,
                                     passport=patient.passport, contact=patient.contact, pin_yin=patient.pin_yin)
        order_patient.save()
        order.patient_order = order_patient
        order.status = -1
        order.save()
        return redirect('order_patient_info')


@login_required
def order_document_info(request):
    order_id = request.session['order_id']
    order_expire(order_id)
    if request.method == 'GET':
        order = Order.objects.get(id=order_id)
        customer = Customer.objects.get(user=request.user)
        appointment_form = AppointmentInfo(instance=customer, initial={
            'hospital': order.hospital.name,
            'hospital_address': order.hospital.area,
            'time': order.submit,
            'name': order.disease.name,
            'diagnose_hospital': order.patient_order.diagnose_hospital if order.patient_order is not None else '',
            'doctor': order.patient_order.doctor if order.patient_order is not None else '',
            'contact': order.patient_order.contact if order.patient_order is not None else '',
        })
        form = create_form(int(order.hospital.id), int(order.disease.id), appointment_form)
        modify_form(order, form)
        return render(request, 'order_document_info.html', {
            'customer': customer,
            'form': form,
            'time': (datetime.datetime.now(tz=pytz.utc) - order.submit).total_seconds(),
            'documents': Document.objects.filter(order=order, type=0)
        })
    else:
        order = Order.objects.get(id=order_id)
        customer = Customer.objects.get(user=request.user)
        form = AppointmentInfo(request.POST, request.FILES, instance=customer)
        if not form.is_valid():
            return render(request, 'order_document_info.html', {
                'form': form,
                'customer': customer,
                'time': (datetime.datetime.now(tz=pytz.utc) - order.submit).total_seconds(),
            })
        required, optional = get_fields(order.hospital.id, order.disease.id)

        for field in required:
            for f in request.FILES.getlist(field):
                doc = Document(document=f, description=field, order=order, type=0)
                doc.save()
        for field in optional:
            for f in request.FILES.getlist(field):
                doc = Document(document=f, description=field, order=order, type=0)
                doc.save()
        doctor = form.cleaned_data.get('doctor')
        hospital = form.cleaned_data.get('diagnose_hospital')
        contact = form.cleaned_data.get('contact')
        patient = order.patient_order
        patient.doctor = doctor
        patient.diagnose_hospital = hospital
        patient.contact = contact
        patient.save()
        order.status = -2
        order.save()
        return redirect('order_review')


@login_required
def order_review(request):
    order_id = request.session['order_id']
    order_expire(order_id)
    customer = Customer.objects.get(user=request.user)
    order = Order.objects.get(id=order_id)
    return render(request, 'order_review.html', {
        'order': order,
        'document': Document.objects.filter(order=order, type=0),
        'customer': customer,
        'time': (datetime.datetime.now(tz=pytz.utc) - order.submit).total_seconds(),
    })


@login_required
def pay_deposit(request):
    order_id = request.session['order_id']
    order_expire(order_id)
    customer = Customer.objects.get(user=request.user)
    order = Order.objects.get(id=order_id)
    order.status = -3
    order.save()
    if request.method == 'POST':
        amount = request.POST.get('amount')
        if int(amount) == -1:
            order.full_payment_paid = False
        else:
            order.full_payment_paid = True
        order.status = 1
        order.save()
        return redirect('order_finish')
    return render(request, 'order_deposit.html', {
        'order': order,
        'customer': customer,
        'time': (datetime.datetime.now(tz=pytz.utc) - order.submit).total_seconds(),
    })


@login_required
def finish(request):
    order_id = request.session['order_id']
    order = Order.objects.get(id=order_id)
    customer = Customer.objects.get(user=request.user)
    auto_assign(order)
    return render(request, 'order_finish.html', {
        'customer': customer,
        'time': (datetime.datetime.now(tz=pytz.utc) - order.submit).total_seconds(),
    })


@login_required
def like_hospital(request):
    customer = Customer.objects.get(user=request.user)
    hospital_id = int(request.POST.get('hospital_id', None))
    disease_id = int(request.POST.get('disease_id', None))
    mark = True if request.POST.get('mark', 'false') == 'true' else False
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


@login_required
def order_check(request):
    order_id = request.session['order_id']
    orders = Order.objects.filter(id=order_id)
    if len(orders) > 0:
        return JsonResponse({'exist': True})
    return JsonResponse({'exist': False})


@login_required
def delete_document(request):
    document_id = request.POST.get('document_id', None)
    try:
        document = Document.objects.get(id=document_id)
        document.delete()
    except Document.DoesNotExist:
        pass
    return JsonResponse({'status': 'deleted'})


def order_expire(order_id):
    if len(Order.objects.filter(id=order_id)) <= 0:
        return TemplateView(template_name='order_expire.html')
