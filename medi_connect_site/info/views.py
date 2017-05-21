from django.shortcuts import render
from customer.models import Customer

# Create your views here.
def profile(request, id):
    customer = Customer.objects.get(id=id)
    return render(request, 'info_profile.html', {
        'customer': customer,
    })