from django import forms
from helper.models import Order, Patient, Disease, Document
from django.core.exceptions import ValidationError


class OrderFormFirst(forms.ModelForm):
    class Meta:
        model = Patient
        exclude = []
        fields = ['name', 'age', 'gender', 'diagnose_hospital']

    def __init__(self, *args, **kwargs):
        super(OrderFormFirst, self).__init__(*args, **kwargs)
        self.fields['diagnose_hospital'].widget.attrs['readonly'] = True

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
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super(OrderFormSecond, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['readonly'] = True

    def clean_category(self):
        category = self.cleaned_data['name']
        if category is None or len(category) == 0:
            raise ValidationError('name cannot be None')
        return category


class DocumentForm(forms.ModelForm):
    document = forms.FileField(
        label="Choose required document",
        required=True,
    )
    extra_document = forms.FileField(
        label="Choose optional document",
        required=False,
    )
    document_comment = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Leave comment for your main document (optional)",
        required=False,
    )
    extra_document_comment = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Leave comment for your extra document (optional)",
        required=False,
    )
    document_description = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Leave description for your main document",
        required=True,
    )
    extra_document_description = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Leave description for your extra document",
        required=False,
    )

    class Meta:
        model = Document
        fields = []
        exclude = []

    def __init__(self, *args, **kwargs):
        super(DocumentForm, self).__init__(*args, **kwargs)
        self.field_order = [
            'document_description',
            'document',
            'document_comment',
            'extra_document_description',
            'extra_document',
            'extra_document_comment',
        ]
        self.order_fields(self.field_order)
