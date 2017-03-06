from django.shortcuts import render_to_response, render
from django.contrib import auth as login_auth

# Create your views here


def home(request):
    return render_to_response('index.html')


def login(request):
    return render(request, 'login.html')


def signup(request):
    return render_to_response('signup.html')


def auth(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = login_auth.authenticate(username=username, password=password)
        if user is not None and user.is_active:
            login_auth.login(request, user)
            return render_to_response('signup.html')
        else:
            return render_to_response('signup.html')
