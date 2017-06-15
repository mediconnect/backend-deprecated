from django.shortcuts import render
from django.http import HttpRequest
from customer.models import Customer
from helper.models import Order
from django.contrib.auth.decorators import login_required
from forms import ProfileForm, PasswordResetForm
from django.contrib.auth.hashers import check_password, make_password


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
def profile_password(request, id):
    customer = Customer.objects.get(id=id)
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
def order(request, id):
    customer = Customer.objects.get(id=id)
    orders = Order.objects.filter(customer=customer)
    order_list = []
    for od in orders:
        order_list.append(od) if od not in order_list else None
    print order_list
    for od in order_list:
        print od.disease.name
        print od.patient.name
        print od.hospital.name
    return render(request, 'info_order.html', {
        'order_list': order_list,
        'customer': customer,
    })
