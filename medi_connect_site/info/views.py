from django.shortcuts import render
from customer.models import Customer
from helper.models import Order
from django.contrib.auth.decorators import login_required


# Create your views here.
@login_required
def profile(request, id):
    customer = Customer.objects.get(id=id)
    return render(request, 'info_profile.html', {
        'customer': customer,
    })


@login_required
def order(request, id):
    customer = Customer.objects.get(id=id)
    order_list = Order.objects.filter(customer=customer)
    return render(request, 'info_order.html', {
        'order_list': order_list,
        'customer': customer,
    })
