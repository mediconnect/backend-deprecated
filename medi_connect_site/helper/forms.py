from django import forms
from helper.models import Order, Patient, Disease


class OrderFormFirst(forms.ModelForm):
    class Meta:
        model = Patient
        exclude = []
        fields = ['name', 'age', 'gender']


class OrderFormSecond(forms.ModelForm):
    class Meta:
        model = Disease
        exclude = []
        fields = ['category']
