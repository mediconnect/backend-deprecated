from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.db.models import Q
from django.http import JsonResponse
from forms import SignUpForm, SearchForm
from customer.models import Customer
from customer.views import customer
from helper.models import Hospital, Disease


# Create your views here


def home(request):
    if request.user.is_authenticated():
        # render a user specified web page
        # assign administrator as super user
        # assign translator as staff
        if request.user.is_superuser:
            print "Need administration module"
        elif request.user.is_staff:
            print "Need translator module"
        else:
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
            firstname = form.cleaned_data.get('first_name')
            lastname = form.cleaned_data.get('last_name')
            telephone = form.cleaned_data.get('telephone')
            address = form.cleaned_data.get('address')
            zipcode = form.cleaned_data.get('zipcode')
            User.objects.create_user(username=username, password=password,
                                     email=email, first_name=firstname, last_name=lastname)
            user = authenticate(username=username, password=password)
            login(request, user)
            customer = Customer(user=user)
            customer.set_attributes(telephone, address, zipcode)
            customer.save()
            return redirect('/')

    else:
        return render(request, 'signup.html',
                      {'form': SignUpForm()})


def search(request):
    # check if request is Ajax or not
    if request.is_ajax():
        querystring = request.GET.get('query', None)
        if querystring is None:
            return JsonResponse({'error_message': 'Please type correct keywords'})

        results = dict()
        results['disease'] = Disease.objects.filter(Q(keyword__icontains=querystring))
        results['hospital'] = Hospital.objects.filter(Q(introduction__icontains=querystring))
        if results['hospital'].count() <= 0 and results['disease'].count() <= 0:
            return JsonResponse({'error_message': 'Not Found'})

        result_json = {}
        index = 1
        for hospital in results['hospital']:
            result_json.update({'hospital' + str(index): str(hospital.name)})
            index += 1
        return JsonResponse(result_json)
    else:
        if request.method == 'POST':
            print 2
            return redirect('/result')
        else:
            return render(request, 'search.html')


def result(request):
    form = SearchForm(request.GET)
    if not form.is_valid():
        print 1
        return redirect('/search', {'form': form})
    else:
        query = form.cleaned_data.get('query')
        hospital_info = {}
        diseases = Disease.objects.filter(Q(keyword__icontains=query))
        for disease in diseases:
            hospitals = Hospital.objects.filter(Q(introduction__icontains=disease.keyword))
            for hospital in hospitals:
                if hospital not in hospital_info:
                    hospital_info.update({hospital: {}})
                    hospital_info[hospital].update({'name': hospital.name})
                    hospital_info[hospital].update({'area': hospital.area})
                    hospital_info[hospital].update({'website': hospital.website})
                    hospital_info[hospital].update({'introduction': hospital.introduction})
    return render(request, 'result.html', )