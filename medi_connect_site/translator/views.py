from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from models import Translator
from helper.models import Document,Order




#Create your views here.

@login_required

def translator(request,user):
    translator = Translator.objects.get(user = user)
    return render(request,'main.html',
    	{
    		'translator':translator
    	})