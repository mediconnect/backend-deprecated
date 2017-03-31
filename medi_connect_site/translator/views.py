from django.contrib.auth.decorators import login_required
from django.shortcuts import render


# Create your views here.
def translator(request):
	return render(request, "translator/main.html",{})
