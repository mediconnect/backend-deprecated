from django.shortcuts import render
from models import Hospital
from customer.models import Customer
from django.contrib.auth.decorators import login_required
from django.db.models import Q


# Create your views here.
@login_required
def hospital(request, name):
    hosp = Hospital.objects.get(name=name)
    return render(request, "hospital_order.html", {
        'hospital': hosp,
        'customer': Customer.objects.get(user=request.user),
    })
