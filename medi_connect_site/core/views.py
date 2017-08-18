from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.db.models import Q
from forms import SignUpForm, SearchForm, ContactForm
from customer.models import Customer
from customer.views import customer
from translator.views import translator
from supervisor.views import supervisor
from helper.models import Hospital, Disease, Staff, Rank
import smtplib


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
    """
    :param request:
    :return:
    this method fetch diseases keyword and compare with user input. the matching
    part can be improved later. if found multiple matching diseases, return
    multiple options and let user choose. if no result, return all diseases and
    let user choose. if exactly one disease is found, directly go to relevant hospital.
    """
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if not form.is_valid():
            return customer(request, request.user)
        else:
            query = form.cleaned_data.get('query')
            dis_list = Disease.objects.all()
            dis = []
            for unit in dis_list:
                keywords = unit.keyword.split(',')
                for keyword in keywords:
                    if str(keyword) in query:
                        dis.append(unit)
                        break

            if len(dis) == 0:
                return render(request, 'disease_choice.html', {
                    'customer': Customer.objects.get(user=request.user),
                    'disease_list': Disease.objects.all(),
                })

            if len(dis) > 1:
                return render(request, 'disease_choice.html', {
                    'customer': Customer.objects.get(user=request.user),
                    'disease_list': dis,
                })

            rank_list = Rank.objects.filter(disease=dis[0]).order_by('rank')
            hospital_list = []
            for r in rank_list:
                hospital_list.append(r.hospital)
                if len(hospital_list) >= 5:
                    break

            return render(request, 'result.html', {
                'hospital_list': hospital_list,
                'disease': dis[0],
                'hospital_length': len(hospital_list) > 0,
                'disease_length': dis is not None,
                'customer': Customer.objects.get(user=request.user)
            })
    else:
        return render(request, 'result.html')


def choose_hospital(request, disease_id):
    dis = Disease.objects.get(id=disease_id)
    rank_list = Rank.objects.filter(disease=dis)
    hospital_list = []
    for r in rank_list:
        hospital_list.append(r.hospital)
        if len(hospital_list) >= 5:
            break

    return render(request, 'result.html', {
        'hospital_list': hospital_list,
        'disease': dis,
        'hospital_length': len(hospital_list) > 0,
        'disease_length': dis is not None,
        'customer': Customer.objects.get(user=request.user)
    })


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


def contact(request):
    form = ContactForm()
    if request.user.is_authenticated():
        customer = Customer.objects.get(user=request.user)
        form.initial.update({'email': customer.user.email})
        return render(request, 'contact.html', {
            'customer': customer,
            'form': form,
        })
    else:
        return render(request, 'contact.html', {
            'form': form,
        })


def send_response(request):
    form = ContactForm(request.POST)
    if not form.is_valid():
        if request.user.is_authenticated():
            return render(request, 'contact.html', {
                'customer': Customer.objects.get(user=request.user),
                'form': form,
            })
        else:
            return render(request, 'contact.html', {
                'form': form,
            })
    email = form.cleaned_data.get('email')
    message = form.cleaned_data.get('message')
    password = 'passwordABC'

    sender = 'abcdefgdontreplyme@outlook.com'
    receivers = [email]
    cc = ['cjs08091996@outlook.com']

    try:
        buf = smtplib.SMTP('smtp-mail.outlook.com', 587)
        buf.ehlo()
        buf.starttls()
        buf.login(sender, password)
        buf.sendmail(sender, receivers + cc, message)
        buf.close()
        print "Successfully sent email"
    except smtplib.SMTPException:
        print "Error: unable to send email"

    return redirect('home')
