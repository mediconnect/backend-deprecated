from django import forms
from helper.models import Order, Patient, Disease, Document
from django.core.exceptions import ValidationError


class PatientInfo(forms.ModelForm):
    class Meta:
        model = Patient
        exclude = []
        fields = ['name', 'age', 'gender', 'diagnose_hospital', 'relationship', 'passport']

    def __init__(self, *args, **kwargs):
        super(PatientInfo, self).__init__(*args, **kwargs)
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


class AppointmentInfo(forms.ModelForm):
    hospital = forms.CharField(
        label="Hospital",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True,
    )

    hospital_address = forms.CharField(
        label="Hospital Address",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True,
    )

    time = forms.DateTimeField(
        label="Appointment Time",
        widget=forms.DateTimeInput(attrs={'class': 'form-control'}),
        required=True,
    )

    class Meta:
        model = Order
        exclude = []
        fields = []

    def __init__(self, *args, **kwargs):
        super(AppointmentInfo, self).__init__(*args, **kwargs)
        self.fields['hospital'].widget.attrs['readonly'] = True
        self.fields['hospital_address'].widget.attrs['readonly'] = True
        self.fields['time'].widget.attrs['readonly'] = True


class DiseaseInfo(forms.ModelForm):
    hospital = forms.CharField(
        label="Hospital in China",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True,
    )

    doctor = forms.CharField(
        label="Doctor",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True,
    )

    contact = forms.CharField(
        label="Contact Info",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True,
    )

    class Meta:
        model = Disease
        exclude = []
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super(DiseaseInfo, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['readonly'] = True
        self.field_order = [
            'name',
            'hospital',
            'doctor',
            'contact',
        ]
        self.order_fields(self.field_order)


class DocumentInfo(forms.ModelForm):
    document = forms.FileField(
        label="Choose required document",
        widget=forms.ClearableFileInput(attrs={'multiple': True}),
        required=True,
    )
    document_comment = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Leave comment for your main document (optional)",
        required=False,
    )
    document_description = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Leave description for your main document",
        required=True,
    )

    class Meta:
        model = Document
        exclude = []
        fields = []

    def __init__(self, *args, **kwargs):
        super(DocumentInfo, self).__init__(*args, **kwargs)
        self.field_order = [
            'document_description',
            'document',
            'document_comment',
        ]
        self.order_fields(self.field_order)
