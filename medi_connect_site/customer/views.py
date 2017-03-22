from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from models import Customer


# Create your views here.
@login_required
def customer(request, user):
    customer = Customer.objects.filter(user=user)
    return render(request, 'customer.html', {'customer': customer})
