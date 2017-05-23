from django.shortcuts import render, HttpResponse
from models import Hospital, Patient, Disease, Order
from customer.models import Customer
from django.contrib.auth.decorators import login_required
from helper.forms import OrderFormFirst, OrderFormSecond


# Create your views here.
@login_required
def hospital(request, name):
    hosp = Hospital.objects.get(name=name)
    order = Order(hospital=hosp, status=1)
    order.save()
    print order.id
    return render(request, "hospital_order.html", {
        'hospital': hosp,
        'customer': Customer.objects.get(user=request.user),
        'order_id': order.id,
    })


@login_required
def order_info_first(request, order_id):
    customer = Customer.objects.get(user=request.user)
    order = Order.objects.get(id=order_id)
    order.customer_id = customer.id
    order.save()
    return render(request, 'order_info_first.html', {
        'customer': customer,
        'form': OrderFormFirst(),
        'order_id': order.id,
    })


@login_required
def order_submit_first(request, order_id):
    form = OrderFormFirst(request.POST)
    order = Order.objects.get(id=order_id)
    if not form.is_valid():
        return render(request, 'order_info_first.html', {
            'form': form,
            'order_id': order.id,
        })
    else:
        name = form.cleaned_data.get('name')
        age = form.cleaned_data.get('age')
        gender = form.cleaned_data.get('gender')
        customer = Customer.objects.get(user=request.user)
        patient = Patient(name=name, age=age, gender=gender, customer=customer)
        patient.save()
        order.patient_id = patient.id
        order.save()
        return render(request, 'order_info_second.html', {
            'customer': customer,
            'form': OrderFormSecond(),
            'order_id': order.id,
        })


@login_required
def order_submit_second(request, order_id):
    form = OrderFormSecond(request.POST)
    order = Order.objects.get(id=order_id)
    if not form.is_valid():
        return render(request, 'order_info_second.html', {
            'form': form,
            'order_id': order.id,
        })
    else:
        category = form.cleaned_data.get('category')
        disease = Disease(category=category)
        disease.save()
        order.disease_id = disease.id
        order.status = 2
        order.save()
        return render(request, 'order_review.html', {
            'order': order,
        })
