from django.shortcuts import render, HttpResponse

# Create your views here.
def profile(request, id):
    return HttpResponse("hello")