from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from helper.models import Document, Order

class AssignmentSummaryForm(forms.ModelForm):
	class Meta:
		model = Document
		fields = ['document']
