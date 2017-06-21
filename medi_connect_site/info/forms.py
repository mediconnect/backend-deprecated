from django import forms
from django.contrib.auth.models import User
from customer.models import Customer
from django.core.exceptions import ValidationError


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        exclude = []
        fields = ['first_name', 'last_name', 'email']
