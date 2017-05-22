from django.shortcuts import render, HttpResponse
from models import Hospital
from customer.models import Customer
from django.contrib.auth.decorators import login_required
from helper.forms import OrderFormFirst


# Create your views here.
@login_required
def hospital(request, name):
    hosp = Hospital.objects.get(name=name)
    return render(request, "hospital_order.html", {
        'hospital': hosp,
        'customer': Customer.objects.get(user=request.user),
    })


def order_info_first(request):
    return render(request, 'order_info_first.html', {
        'form': OrderFormFirst()
    })
