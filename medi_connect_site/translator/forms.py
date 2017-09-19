from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from helper.models import Document, Order

class AssignmentSummaryForm(forms.ModelForm):
	class Meta:
		model = Document
		fields = ['document']

class StaffLoginForm(forms.ModelForm):
    class Meta:
        model = User
        exclude = []
        fields = ['email', 'password']

    def __init__(self, *args, **kwargs):
        super(StaffLoginForm, self).__init__(*args, **kwargs)
        self.fields['password'].widget = forms.PasswordInput()