from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from models import Translator
from helper.models import Document,Order
from django.core.files.storage import FileSystemStorage
from forms import TransUploadForm




#Create your views here.

@login_required

def translator_id(request,id):
    translator = Translator.objects.get(id= id)
    assignments = Document.objects.filter(translator_id = id)
    assignments.order_by('assign_time')
    return render(request,'trans_home.html',
    	{
    		'assignments': assignments,
    		'translator': translator

    	})

@login_required
def translator(request,user):
    translator = Translator.objects.get(user= user)
    assignments = Document.objects.filter(translator_id = translator.id)
    assignments.order_by('assign_time')
    return render(request,'trans_home.html',
    	{
    		'assignments': assignments,
    		'translator': translator

    	})

@login_required
def upload(request,id):
	translator = Translator.objects.get(id = id)
	if request.method == 'POST':
		form = TransUploadForm(request.POST,request.FILES)
		if form.is_valid():
			order_id = form.cleaned_data.get('order_id')
			file = form.cleaned_data.get('document')
			translator_id = translator.id
			document = Document
			return redirect ('translator_home')
	else:
		form = TransUploadForm()
	return render(request,'upload.html',
		{
			'form':form,
			'translator':translator

		})