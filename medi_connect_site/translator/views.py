from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from models import Translator
from helper.models import Document,Order
from django.core.files.storage import FileSystemStorage
from forms import TransUploadForm




#Create your views here.

@login_required

def translator(request,user):
    translator = Translator.objects.get(user = user)
    assignments = Document.objects.filter(translator_id = translator)
    assignments.order_by('assign_time')
    return render(request,'home.html',
    	{
    		'assignments': assignments

    	})

def upload(request):
	if request.method == 'POST':
		form = TransUploadForm(request.POST,request.FILES)
		if form.is_valid():
			form.save()
			return redirect ('translator_home')
		else:
			form = TransUploadForm()
		return render(request,'upload.html',{
			'form':form
			})