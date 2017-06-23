from django import forms
from helper.models import Order, Patient, Disease, Document
from django.core.exceptions import ValidationError


class OrderFormFirst(forms.ModelForm):
    class Meta:
        model = Patient
        exclude = []
        fields = ['name', 'age', 'gender']

    def clean_name(self):
        name = self.cleaned_data['name']
        if name is None or len(name) == 0:
            raise ValidationError('name cannot be None')
        return name

    def clean_age(self):
        age = self.cleaned_data['age']
        if age is None:
            raise ValidationError('age cannot be None')
        if age < 0:
            raise ValidationError('please enter correct age')
        return age

    def clean_gender(self):
        gender = self.cleaned_data['gender']
        if gender is None or len(gender) == 0:
            raise ValidationError('gender cannot be None')
        return gender


class OrderFormSecond(forms.ModelForm):
    class Meta:
        model = Disease
        exclude = []
        fields = ['category']

    def clean_category(self):
        category = self.cleaned_data['category']
        if category is None or len(category) == 0:
            raise ValidationError('category cannot be None')
        return category


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        exclude = []
        fields = ['document']

    def __init__(self, *args, **kwargs):
        super(DocumentForm, self).__init__(*args, **kwargs)
