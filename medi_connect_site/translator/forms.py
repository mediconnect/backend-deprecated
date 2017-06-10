from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from helper.models import Document, Order
from translator.models import Translator
APPROVAL_OPTIONS = ('APPROVE','DISAPPROVE')

class TransUploadForm(forms.ModelForm):
	order_id = forms.ModelChoiceField(queryset = Order.objects.all())
	class Meta:
		model = Document
		fields = ['description','order_id','document']

