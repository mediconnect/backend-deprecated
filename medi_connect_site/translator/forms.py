from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from helper.models import Document
from translator.models import Translator
APPROVAL_OPTIONS = ('APPROVE','DISAPPROVE')

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ( 'document')

