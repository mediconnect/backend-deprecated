from django import forms
from helper.models import Order, Patient


class OrderFormFirst(forms.ModelForm):
    class Meta:
        model = Patient
        exclude = []
        fields = ['name', 'age', 'gender']


class OrderFormSecond(forms.ModelForm):
    disease_category = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=30,
        label='Category of disease',
        required=True,
    )

