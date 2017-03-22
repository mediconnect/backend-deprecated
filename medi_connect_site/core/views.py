from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from forms import SignUpForm
from customer.models import Customer
from customer.views import customer


# Create your views here


def home(request):
    if request.user.is_authenticated():
        # render a user specified web page
        return customer(request, request.user)
    else:
        return render(request, 'index.html')


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if not form.is_valid():
            return render(request, 'signup.html',
                          {'form': form})
        else:
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            User.objects.create_user(username=username, password=password,
                                     email=email)
            user = authenticate(username=username, password=password)
            login(request, user)
            customer = Customer(user=user)
            customer.save()
            return redirect("/")

    else:
        return render(request, 'signup.html',
                      {'form': SignUpForm()})
