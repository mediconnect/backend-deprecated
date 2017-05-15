from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from models import Customer
from core.forms import SearchForm


# Create your views here.
@login_required
def customer(request, user):
    customer = Customer.objects.get(user=user)
    return render(request, 'customer.html',
                  {
                      'customer': customer,
                      'form': SearchForm()
                  })
