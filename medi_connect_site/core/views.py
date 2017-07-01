from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.db.models import Q
from forms import SignUpForm, SearchForm
from customer.models import Customer
from customer.views import customer
from translator.views import translator
from supervisor.views import supervisor
from helper.models import Hospital, Disease, Order


# Create your views here


def home(request):
    if request.user.is_authenticated():
        # render a user specified web page
        # assign administrator as super user
        # assign translator as staff
        if request.user.is_superuser:
            return supervisor(request, request.user.id)
        elif request.user.is_staff:
            return translator(request, request.user.id)
        else:
            return customer(request, request.user)
    else:
        return render(request, 'index.html', {
            'form': SearchForm()
        })


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
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            telephone = form.cleaned_data.get('telephone')
            address = form.cleaned_data.get('address')
            zipcode = form.cleaned_data.get('zipcode')
            User.objects.create_user(username=username, password=password,
                                     email=email, first_name=first_name, last_name=last_name)
            user = authenticate(username=username, password=password)
            login(request, user)
            customer = Customer(user=user)
            customer.set_attributes(telephone, address, zipcode)
            customer.save()
            return redirect('/')

    else:
        return render(request, 'signup.html',
                      {'form': SignUpForm()})


def result(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if not form.is_valid():
            return customer(request, request.user)
        else:
            query = form.cleaned_data.get('query')
            dis = Disease.objects.filter(Q(keyword__icontains=query))
            for unit in dis:
                keywords = set(unit.keyword.split(','))
                if query in keywords:
                    dis = unit
                    break

            hospital_info = []
            hospitals = Hospital.objects.filter(Q(specialty__icontains=query))
            for hosp in hospitals:
                specialities = set(hosp.specialty.split(','))
                if query in specialities:
                    hospital_info.append(hosp)

            if request.user.is_authenticated():
                return render(request, 'result.html',
                              {
                                  'hospital_list': hospital_info,
                                  'disease': dis,
                                  'customer': Customer.objects.get(user=request.user)
                              })
    else:
        return render(request, 'result.html')


def result_guest(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if not form.is_valid():
            return render(request, 'index.html', {
                'form': SearchForm()
            })
        else:
            query = form.cleaned_data.get('query')
            hospital_info = []
            hospitals = Hospital.objects.filter(Q(specialty__icontains=query))
            for hosp in hospitals:
                hospital_info.append(hosp) if hosp not in hospital_info else None

            return render(request, 'result_guest.html',
                          {
                              'hospital_list': hospital_info,
                          })
    else:
        return render(request, 'result_guest.html')


def disease(request):
    diseases = Disease.objects.all()
    return render(request, 'disease.html', {
        'diseases': diseases,
    })


def hospital(request):
    hospitals = Hospital.objects.order_by('rank')[0:20]
    return render(request, 'hospital.html', {
        'hospitals': hospitals,
    })
