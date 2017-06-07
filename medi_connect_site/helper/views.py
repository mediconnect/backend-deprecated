from django.shortcuts import render, redirect
from models import Hospital, Patient, Disease, Order, Document
from customer.models import Customer
from django.contrib.auth.decorators import login_required
from helper.forms import OrderFormFirst, OrderFormSecond, DocumentForm


# Create your views here.
@login_required
def hospital(request, name):
    hosp = Hospital.objects.get(name=name)
    customer = Customer.objects.get(user=request.user)
    order_list = Order.objects.filter(customer=customer)
    order = None
    for each in order_list:
        if hosp == each.hospital and each.status == str(0):
            order = each
    order = Order(hospital=hosp, status=0) if order is None else order
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
            'form': OrderFormFirst(),
            'order_id': order.id,
        })
    elif order.disease is None or order.disease.category is None or len(order.disease.category) == 0:
        return redirect('order_submit_first', order_id=order_id)
    else:
        return redirect('order_submit_second', order_id=order_id)


@login_required
def order_submit_first(request, order_id):
    if request.method == 'POST':
        form = OrderFormFirst(request.POST)
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
            patient = Patient(name=name, age=age, gender=gender, customer=customer)
            patient.save()
            order.patient = patient
            order.status = 0
            order.save()
            return render(request, 'order_info_second.html', {
                'customer': customer,
                'form': OrderFormSecond(),
                'order_id': order.id,
            })
    else:
        customer = Customer.objects.get(user=request.user)
        return render(request, 'order_info_second.html', {
            'customer': customer,
            'form': OrderFormSecond(),
            'order_id': order_id,
        })


@login_required
def order_submit_second(request, order_id):
    if request.method == 'POST':
        form = OrderFormSecond(request.POST)
        order = Order.objects.get(id=order_id)
        customer = Customer.objects.get(user=request.user)
        if not form.is_valid():
            return render(request, 'order_info_second.html', {
                'form': form,
                'order_id': order.id,
                'customer': customer,
            })
        else:
            category = form.cleaned_data.get('category')
            disease = Disease(category=category)
            disease.save()
            order.disease = disease
            order.save()
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
        form = DocumentForm(request.POST)
        if not form.is_valid():
            return render(request, 'document_submit.html', {
                'form': form,
                'order_id': order.id,
                'customer': customer,
            })
        else:
            document = form.cleaned_data.get('document')
            document_trans = form.cleaned_data.get('document_trans')
            doc = Document(document=document, document_trans=document_trans)
            doc.order = order
            doc.save()
            order.hospital.slots_open -= 1
            order.hospital.save()
            order.status = 1
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