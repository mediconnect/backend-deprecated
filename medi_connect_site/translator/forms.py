from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from helper.models import Document
from translator.models import Translator,Supervisor

APPROVAL_OPTIONS = ('APPROVE','DISAPPROVE')
class CheckForm(forms.Form,document):
	document = Document.objects.get(id = document)
	approved = forms.BooleanField()

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ( 'document')

