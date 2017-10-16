#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.shortcuts import render, redirect
from customer.models import Customer
from helper.models import Order, Patient, Document, LikeHospital, Hospital, Disease, HospitalReview,auto_assign
from django.contrib.auth.decorators import login_required
from forms import ProfileForm, PasswordResetForm, PatientAddForm, DocAddForm
from django.contrib.auth.hashers import check_password, make_password
from django.utils.http import urlquote
from django.template.defaultfilters import register


# Create your views here.
@login_required
def profile(request):
    customer = Customer.objects.get(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST)
        if not form.is_valid():
            return render(request, 'info_profile.html', {
                'customer': customer,
                'form': form,
            })
        first_name = form.cleaned_data.get('first_name')
        last_name = form.cleaned_data.get('last_name')
        email = form.cleaned_data.get('email')
        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()

        customer.user = user
        tel = form.cleaned_data.get('tel')
        address = form.cleaned_data.get('address')
        wechat = form.cleaned_data.get('wechat')
        customer.tel = tel
        customer.address = address
        customer.wechat = wechat
        customer.save()
    form = ProfileForm(instance=request.user, initial={
        'email': request.user.email,
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'tel': customer.tel,
        'address': customer.address,
        'wechat': customer.wechat
    })
    return render(request, 'info_profile.html', {
        'customer': customer,
        'form': form,
    })


@login_required
def profile_password(request):
    customer = Customer.objects.get(user=request.user)
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if not form.is_valid():
            return render(request, 'info_profile_password.html', {
                'customer': customer,
                'form': form
            })
        old_password = form.cleaned_data.get('old_password')
        user = customer.user
        if not check_password(old_password, user.password, preferred='default'):
            form.add_error('old_password', 'password doesn\'t match with previous password')
            return render(request, 'info_profile_password.html', {
                'customer': customer,
                'form': form
            })
        password = form.cleaned_data.get('password')
        user.password = make_password(password)
        user.save()
        customer.save()
    return render(request, 'info_profile_password.html', {
        'customer': customer,
        'form': PasswordResetForm()
    })


@login_required
def profile_patient(request):
    customer = Customer.objects.get(user=request.user)
    patients = Patient.objects.filter(customer=customer)
    if request.method == 'POST':
        form = PatientAddForm(request.POST)
        if not form.is_valid():
            return render(request, 'info_profile_patient.html', {
                'customer': customer,
                'form': form,
                'patients': patients,
            })
        first_name = form.cleaned_data.get('first_name')
        last_name = form.cleaned_data.get('last_name')
        birth = form.cleaned_data.get('birth')
        gender = form.cleaned_data.get('gender')
        patient = Patient.objects.create(first_name=first_name, last_name=last_name, birth=birth, gender=gender,
                                         customer=customer)
        patient.save()
    patients = Patient.objects.filter(customer=customer)
    return render(request, 'info_profile_patient.html', {
        'customer': customer,
        'patients': patients,
        'patients_length': len(patients) > 0,
        'form': PatientAddForm()
    })


@login_required
def order(request):
    customer = Customer.objects.get(user=request.user)
    orders = Order.objects.filter(customer=customer)
    order_list = []
    status_dict = [u'未提交', u'未付款', u'翻译中', u'翻译中',
                   u'医院研究反馈中', u'医院研究反馈中', u'医院研究反馈中',
                   u'医院反馈翻译完成', u'订单完成']
    for order in orders:
        if int(order.status) == 8:
            continue
        order_dict = dict()
        order_dict['patient'] = order.patient_order.get_name() if order.patient_order is not None else 'unknown'
        order_dict['time'] = str(order.submit)
        order_dict['disease'] = order.disease.name if order.disease is not None else 'unknown'
        order_dict['hospital'] = order.hospital.name if order.hospital is not None else 'unknown'
        order_dict['status'] = status_dict[int(order.status)] if order.status is not None else 0
        order_dict['id'] = int(order.id)
        order_list.append(order_dict)
    return render(request, 'info_order.html', {
        'orders': order_list,
        'order_length': len(order_list) > 0,
        'customer': customer,
    })


@login_required
def order_finished(request):
    customer = Customer.objects.get(user=request.user)
    orders = Order.objects.filter(customer=customer)
    order_list = []
    status_dict = [u'未提交', u'未付款', u'翻译中', u'翻译中',
                   u'医院研究反馈中', u'医院研究反馈中', u'医院研究反馈中',
                   u'医院反馈翻译完成', u'订单完成']
    for order in orders:
        if int(order.status) != 8:
            continue
        order_dict = dict()
        order_dict['patient'] = order.patient_order.get_name() if order.patient_order is not None else 'unknown'
        order_dict['time'] = str(order.submit)
        order_dict['disease'] = order.disease.name if order.disease is not None else 'unknown'
        order_dict['hospital'] = order.hospital.name if order.hospital is not None else 'unknown'
        order_dict['status'] = status_dict[int(order.status)] if order.status is not None else 0
        order_dict['id'] = int(order.id)
        order_list.append(order_dict)
    return render(request, 'info_order_finished.html', {
        'orders': order_list,
        'order_length': len(order_list) > 0,
        'customer': customer,
    })


@login_required
def order_pay(request, order_id):
    customer = Customer.objects.get(user=request.user)
    order = Order.objects.get(id=order_id)
    return render(request, 'order_pay.html', {
        'order': order,
        'customer': customer,
    })


@login_required
def process_order(request, order_id):
    customer = Customer.objects.get(user=request.user)
    order = Order.objects.get(id=order_id)
    order.status = 2
    auto_assign(order)
    order.save()
    return redirect('info_order', customer.id)


@login_required
def order_detail(request, order_id):
    customer = Customer.objects.get(user=request.user)
    order = Order.objects.get(id=order_id)
    return render(request, 'info_order_detail.html', {
        'customer': customer,
        'order': order,
        'pay': int(order.status) < 2,
    })


def add_doc(request, order_id):
    customer = Customer.objects.get(user=request.user)
    order = Order.objects.get(id=order_id)
    if request.method == 'POST':
        form = DocAddForm(request.POST, request.FILES, instance=customer)
        if not form.is_valid():
            return render(request, 'add_doc.html', {
                'form': form,
                'customer': customer,
                'order': order,
            })
        document = form.cleaned_data.get('document')
        description = form.cleaned_data.get('description')
        comment = form.cleaned_data.get('comment')
        doc = Document(document=urlquote(document), comment=comment,
                       description=description, order=order)
        doc.save()
        order.origin.add(doc)
        return redirect('info_order', customer.id)
    return render(request, 'add_doc.html', {
        'form': DocAddForm(),
        'customer': customer,
        'order': order,
    })


@login_required
def bookmark(request):
    customer = Customer.objects.get(user=request.user)
    liked_hospital = LikeHospital.objects.filter(customer=customer)
    diseases = set()
    for h in liked_hospital:
        diseases.add(h.disease)
    return render(request, 'bookmark.html', {
        'diseases': diseases,
        'customer': customer,
        'disease_length': len(diseases) > 0,
    })


@login_required
def bookmark_compare(request, disease_id):
    customer = Customer.objects.get(user=request.user)
    liked_hospital = LikeHospital.objects.filter(customer=customer)
    disease = Disease.objects.get(id=disease_id)
    hospitals = []
    for h in liked_hospital:
        if h.disease == disease:
            hospitals.append(h.hospital)
    return render(request, 'bookmark_compare.html', {
        'hospitals': hospitals,
        'hospitals_length': len(hospitals) > 0,
        'disease': disease,
        'customer': customer,
    })


@login_required
def unmark(request, hospital_id):
    customer = Customer.objects.get(user=request.user)
    hosp = Hospital.objects.get(id=hospital_id)
    liked_hospital = LikeHospital.objects.filter(customer=customer, hospital=hosp)
    for item in liked_hospital:
        item.delete()
    return redirect('info_bookmark')


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@login_required
def profile_patient_edit(request, patient_id):
    customer = Customer.objects.get(user=request.user)
    patient = Patient.objects.get(id=patient_id)
    if request.method == 'POST':
        form = PatientAddForm(request.POST)
        if not form.is_valid():
            form.add_initial_prefix({
                'name': patient.get_name(),
                'birth': patient.birth,
                'gender': patient.gender,
            })
            return render(request, 'info_profile_patient_edit.html', {
                'customer': customer,
                'form': form,
                'patient': patient,
            })
        patient.first_name = form.cleaned_data.get('first_name')
        patient.last_name = form.cleaned_data.get('last_name')
        patient.birth = form.cleaned_data.get('birth')
        patient.gender = form.cleaned_data.get('gender')
        patient.pin_yin = form.cleaned_data.get('pin_yin')
        patient.save()
        return redirect('info_profile_patient')
    form = PatientAddForm(instance=request.user, initial={
        'name': patient.get_name(),
        'birth': patient.birth,
        'gender': patient.gender,
    })
    return render(request, 'info_profile_patient_edit.html', {
        'customer': customer,
        'form': form,
        'patient': patient,
    })


@login_required
def hospital_review(request, order_id):
    order = Order.objects.get(id=order_id)
    if request.method == 'POST':
        order.status = 8
        order.save()
        score = request.POST.get('score')
        comment = request.POST.get('comment')
        review = HospitalReview(hospital=order.hospital, score=score, comment=comment, order=order)
        review.save()
        return redirect('info_order')
    return render(request, 'info_hospital_review.html', {
        'customer': Customer.objects.get(user=request.user),
        'order': order,
    })
