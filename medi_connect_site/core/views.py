from django.shortcuts import render, redirect, HttpResponseRedirect
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.db.models import Q
from forms import SignUpForm, SearchForm
from customer.models import Customer
from customer.views import customer
from translator.views import translator
from supervisor.views import supervisor
from helper.models import Hospital, Disease, Staff, Rank


# Create your views here


def home(request):
    if request.user.is_authenticated():
        # render a user specified web page
        # role: supervisor = 0, trans_C2E = 1, trnas_E2C = 2
        if request.user.is_staff:
            staff = Staff.objects.get(user_id=request.user.id)
            print staff.get_role()
            if staff.get_role() == 0:
                return supervisor(request, request.user.id)
            else:
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
            dis_list = Disease.objects.filter(Q(keyword__icontains=query))
            dis = None
            for unit in dis_list:
                keywords = set(unit.keyword.split(','))
                if query in keywords:
                    dis = unit
                    break

            rank_list = Rank.objects.filter(disease=dis).order_by('rank')
            hospital_list = []
            for r in rank_list:
                hospital_list.append(r.hospital)
                if len(hospital_list) >= 5:
                    break

            if request.user.is_authenticated():
                return render(request, 'result.html',
                              {
                                  'hospital_list': hospital_list,
                                  'disease': dis,
                                  'hospital_length': len(hospital_list) > 0,
                                  'disease_length': dis is not None,
                                  'customer': Customer.objects.get(user=request.user)
                              })
    else:
        return render(request, 'result.html')


def result_guest(request):
    """
    result guest is search function used for customers not login.
    this function can be optimized in the future, the algorithm of how
    search is implemented.
    """
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if not form.is_valid():
            return render(request, 'index.html', {
                'form': SearchForm()
            })
        else:
            query = form.cleaned_data.get('query')
            dis_list = Disease.objects.filter(Q(keyword__icontains=query))
            dis = None
            for unit in dis_list:
                keywords = set(unit.keyword.split(','))
                if query in keywords:
                    dis = unit
                    break

            rank_list = Rank.objects.filter(disease=dis).order_by('rank')
            hospital_list = []
            for r in rank_list:
                hospital_list.append(r.hospital)
                if len(hospital_list) >= 5:
                    break

            return render(request, 'result_guest.html',
                          {
                              'hospital_list': hospital_list,
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


def username_check(request):
    """
    :param request:
    :return: JsonResponse with exist == True or False
    this method used by front end Ajax call to check if user name exists
    """
    name = request.GET.get('username', None)
    users = User.objects.filter(username=name)
    if len(users) > 0:
        return JsonResponse({'exist': True})
    return JsonResponse({'exist': False})


def email_check(request):
    """
    :param request:
    :return: JsonResponse with exist == True or False
    this method used by front end Ajax call to check if email exists
    """
    name = request.GET.get('email', None)
    users = User.objects.filter(email=name)
    if len(users) > 0:
        return JsonResponse({'exist': True})
    return JsonResponse({'exist': False})
