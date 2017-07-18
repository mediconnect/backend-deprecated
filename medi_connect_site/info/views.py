from django.shortcuts import render, redirect
from customer.models import Customer
from helper.models import Order, Patient, Document, LikeHospital, Hospital
from django.contrib.auth.decorators import login_required
from forms import ProfileForm, PasswordResetForm, PatientAddForm, DocAddForm
from django.contrib.auth.hashers import check_password, make_password
import json
from django.utils.http import urlquote


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
        customer.save()
    form = ProfileForm(instance=request.user, initial={
        'email': request.user.email,
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
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
        name = form.cleaned_data.get('name')
        age = form.cleaned_data.get('age')
        gender = form.cleaned_data.get('gender')
        patient = Patient.objects.create(name=name, age=age, gender=gender, customer=customer)
        patient.save()
    patients = Patient.objects.filter(customer=customer)
    return render(request, 'info_profile_patient.html', {
        'customer': customer,
        'patients': patients,
        'form': PatientAddForm()
    })


@login_required
def order(request):
    customer = Customer.objects.get(user=request.user)
    orders = Order.objects.filter(customer=customer)
    order_list = []
    for order in orders:
        if order.status == 0:
            continue
        order_dict = dict()
        order_dict['hospital'] = order.hospital.name if order.hospital is not None else 'unknown'
        order_dict['disease'] = order.disease.name if order.disease is not None else 'unknown'
        order_dict['patient'] = order.patient.name if order.patient is not None else 'unknown'
        order_dict['order_id'] = order.id
        order_dict['status'] = order.status
        order_dict['trans_status'] = order.trans_status if order.trans_status is not None else 'unknown'
        order_dict['documents'] = []
        for item in order.feedback.all():
            order_dict['documents'].append(item.document.url)
        order_list.append(order_dict)
    return render(request, 'info_order.html', {
        'order_list': json.dumps(order_list),
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
    order.status = 7
    order.save()
    return redirect('info_order', customer.id)


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
    hospitals = []
    for h in liked_hospital:
        hospitals.append(h.hospital)
    return render(request, 'bookmark.html', {
        'hospitals': hospitals,
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
