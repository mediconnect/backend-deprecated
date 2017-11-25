#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from forms import SignUpForm, SearchForm, ContactForm, LoginForm
from customer.models import Customer
from customer.views import customer
from translator.views import translator
from supervisor.views import supervisor
from helper.models import Hospital, Disease, Staff, Rank, Slot, Price
import smtplib
import json


# Create your views here


def home(request):
    if request.user.is_authenticated():
        # render a user specified web page
        # role: supervisor = 0, trans_C2E = 1, trnas_E2C = 2
        if request.user.is_staff:
            staff = Staff.objects.get(user_id=request.user.id)
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


def auth(request):
    # TODO: add more eror info
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if not form.is_valid():
            return render(request, 'login.html',
                          {'form': form})
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')
        user = authenticate(email=email, password=password)
        if user is None:
            return render(request, 'login.html',
                          {
                            'form': form,
                            'error': 'Invalid Login'
                           })
        login(request, user)
        return redirect('/')
    return render(request, 'login.html', {
        'form': LoginForm(),
    })


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if not form.is_valid():
            return render(request, 'signup.html',
                          {'form': form})
        else:
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            telephone = form.cleaned_data.get('telephone')
            address = form.cleaned_data.get('address')
            User.objects.create_user(username=email, password=password,
                                     email=email, first_name=first_name, last_name=last_name)
            user = authenticate(email=email, password=password)
            login(request, user)
            customer = Customer(user=user, tel=telephone, address=address)
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
            exact_match = False
            for unit in dis_list:
                # split according to unicode chinese letter
                keywords = unit.keyword.split(u'\uff0c')
                for keyword in keywords:
                    if keyword in query:
                        exact_match = exact_match or keyword == query
                        dis.append(unit)
                        if exact_match:
                            break

            if len(dis) == 0:
                return render(request, 'disease_choice.html', {
                    'customer': Customer.objects.get(user=request.user),
                    'all_dis': Disease.objects.all(),
                    'disease_length': False,
                })

            if len(dis) > 1 or not exact_match:
                return render(request, 'disease_choice.html', {
                    'customer': Customer.objects.get(user=request.user),
                    'disease_list': dis,
                    'all_dis': Disease.objects.all(),
                    'disease_length': True,
                })

            rank_list = Rank.objects.filter(disease=dis[0]).order_by('rank')
            hospital_list = []
            rank = 1
            for r in rank_list:
                hosp = r.hospital
                single_hopital = dict()
                single_hopital['id'] = hosp.id
                single_hopital['name'] = hosp.name
                single_hopital['rank'] = rank
                single_hopital['score'] = hosp.average_score
                single_hopital['introduction'] = hosp.introduction
                single_hopital['feedback_time'] = hosp.feedback_time
                single_hopital['image'] = hosp.image.url
                single_hopital['full_price'] = Price.objects.get(hospital=hosp, disease=dis[0]).full_price
                single_hopital['deposit_price'] = Price.objects.get(hospital=hosp, disease=dis[0]).deposit
                rank += 1
                slot = Slot.objects.get(disease=dis[0], hospital=hosp)
                single_hopital['slot'] = {0: slot.slots_open_0, 1: slot.slots_open_1, 2: slot.slots_open_2,
                                          3: slot.slots_open_3}
                hospital_list.append(single_hopital)

            return render(request, 'result.html', {
                'hospital_list': hospital_list,
                'disease': dis[0],
                'hospital_length': len(hospital_list) > 0,
                'disease_length': dis is not None,
                'customer': Customer.objects.get(user=request.user),
                'message': u'你是不是在搜索这个疾病: ' + dis[0].name,
            })
    else:
        return render(request, 'result.html')


def choose_hospital(request, disease_id):
    dis = Disease.objects.get(id=disease_id)
    rank_list = Rank.objects.filter(disease=dis).order_by('rank')
    hospital_list = []
    rank = 1
    for r in rank_list:
        hosp = r.hospital
        single_hopital = dict()
        single_hopital['id'] = hosp.id
        single_hopital['name'] = hosp.name
        single_hopital['rank'] = rank
        single_hopital['score'] = hosp.average_score
        single_hopital['introduction'] = hosp.introduction
        single_hopital['feedback_time'] = hosp.feedback_time
        single_hopital['image'] = hosp.image.url
        single_hopital['full_price'] = Price.objects.get(hospital=hosp, disease=dis).full_price
        single_hopital['deposit_price'] = Price.objects.get(hospital=hosp, disease=dis).deposit
        rank += 1
        slot = Slot.objects.get(disease=dis, hospital=hosp)
        single_hopital['slot'] = {0: slot.slots_open_0, 1: slot.slots_open_1, 2: slot.slots_open_2,
                                  3: slot.slots_open_3}
        hospital_list.append(single_hopital)

    if request.user.is_authenticated():
        return render(request, 'result.html', {
            'hospital_list': hospital_list,
            'disease': dis,
            'hospital_length': len(hospital_list) > 0,
            'disease_length': dis is not None,
            'customer': Customer.objects.get(user=request.user)
        })
    else:
        return render(request, 'result_guest.html', {
            'hospital_list': hospital_list,
            'disease': dis,
            'hospital_length': len(hospital_list) > 0,
            'disease_length': dis is not None,
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
                'form': form,
            })
        else:
            query = form.cleaned_data.get('query')
            dis_list = Disease.objects.all()
            dis = []
            exact_match = False
            for unit in dis_list:
                # split according to unicode chinese letter
                keywords = unit.keyword.split(u'\uff0c')
                for keyword in keywords:
                    if keyword in query:
                        exact_match = exact_match or keyword == query
                        dis.append(unit)
                        if exact_match:
                            break

            if len(dis) == 0:
                return render(request, 'disease_choice.html', {
                    'all_dis': Disease.objects.all(),
                    'disease_length': False,
                })

            if len(dis) > 1 or not exact_match:
                return render(request, 'disease_choice.html', {
                    'disease_list': dis,
                    'all_dis': Disease.objects.all(),
                    'disease_length': True,
                })

            rank_list = Rank.objects.filter(disease=dis[0]).order_by('rank')
            hospital_list = []
            rank = 1
            for r in rank_list:
                hosp = r.hospital
                single_hopital = dict()
                single_hopital['id'] = hosp.id
                single_hopital['name'] = hosp.name
                single_hopital['rank'] = rank
                single_hopital['score'] = hosp.average_score
                single_hopital['introduction'] = hosp.introduction
                single_hopital['feedback_time'] = hosp.feedback_time
                single_hopital['image'] = hosp.image.url
                single_hopital['full_price'] = Price.objects.get(hospital=hosp, disease=dis[0]).full_price
                single_hopital['deposit_price'] = Price.objects.get(hospital=hosp, disease=dis[0]).deposit
                rank += 1
                slot = Slot.objects.get(disease=dis[0], hospital=hosp)
                single_hopital['slot'] = {0: slot.slots_open_0, 1: slot.slots_open_1, 2: slot.slots_open_2,
                                          3: slot.slots_open_3}
                hospital_list.append(single_hopital)

            return render(request, 'result.html', {
                'hospital_list': hospital_list,
                'disease': dis[0],
                'hospital_length': len(hospital_list) > 0,
                'disease_length': dis is not None,
                'message': u'你是不是在搜索这个疾病: ' + dis[0].name,
            })
    else:
        return render(request, 'result_guest.html')


def disease(request):
    diseases = Disease.objects.all()
    return render(request, 'disease.html', {
        'diseases': diseases,
    })


def hospital(request):
    hospitals = Hospital.objects.all()[0:20]
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
    """
    :param request:
    :return:
    send customer response to according emails
    """
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

    if request.user.is_authenticated():
        return render(request, 'success.html', {
            'customer': Customer.objects.get(user=request.user)
        })
    return render(request, 'success_guest.html')


def hospital_detail(request, hospital_id):
    return render(request, 'hospital_detail.html', {
        'hospital': Hospital.objects.get(id=hospital_id)
    })
