from django.shortcuts import render
from customer.models import Customer
from helper.models import Order
from django.contrib.auth.decorators import login_required
from forms import ProfileForm


# Create your views here.
@login_required
def profile(request, id):
    customer = Customer.objects.get(id=id)
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
def order(request, id):
    customer = Customer.objects.get(id=id)
    order_list = Order.objects.filter(customer=customer)
    return render(request, 'info_order.html', {
        'order_list': order_list,
        'customer': customer,
    })
