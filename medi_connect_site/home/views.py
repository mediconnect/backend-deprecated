from django.shortcuts import render_to_response


# Create your views here

def home(request):
    return render_to_response('index.html')


def login(request):
    return render_to_response('login.html')


def signup(request):
    return render_to_response('signup.html')
