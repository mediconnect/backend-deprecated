# -*- coding: utf-8 -*-
from django import forms
from django.core.exceptions import ValidationError
from helper.models import Order, Patient, Document
from dynamic_form.forms import get_fields


class PatientInfo(forms.ModelForm):
    # those fields belong to patient
    contact = forms.CharField(
        label="Contact",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False,
    )

    email = forms.EmailField(
        label="Email",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False,
    )

    address = forms.CharField(
        label="Address",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False,
    )

    telephone = forms.CharField(
        label="Tel",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False,
    )

    wechat = forms.CharField(
        label="Wechat",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False,
    )

    qq = forms.CharField(
        label="QQ",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False,
    )

    last_name_pin_yin = forms.CharField(
        label="Last Name Pin Yin",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False,
    )

    first_name_pin_yin = forms.CharField(
        label="First Name Pin Yin",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False,
    )

    class Meta:
        model = Patient
        exclude = []
        fields = ['first_name', 'last_name', 'birth', 'gender', 'relationship', 'passport']

    def __init__(self, *args, **kwargs):
        super(PatientInfo, self).__init__(*args, **kwargs)
        self.fields['contact'].widget.attrs['readonly'] = True
        self.fields['email'].widget.attrs['readonly'] = True
        self.fields['address'].widget.attrs['readonly'] = True
        self.fields['telephone'].widget.attrs['readonly'] = True
        self.fields['wechat'].widget.attrs['readonly'] = True
        self.fields['qq'].widget.attrs['readonly'] = True
        self.fields['birth'].label = 'format should be yy-mm-dd change this later once UI plugin is done'
        # comment out this form for later use
        # self.fields['birth'].widget = forms.DateInput(attrs={'class': 'datepicker'})
        self.fields['first_name'].required = False
        self.fields['last_name'].required = False
        self.fields['birth'].required = False
        self.fields['gender'].required = False
        self.fields['relationship'].required = False
        self.fields['passport'].required = False
        self.field_order = [
            'contact', 'email', 'address', 'telephone', 'wechat', 'qq', 'first_name', 'last_name', 'first_name_pin_yin',
            'last_name_pin_yin'
        ]
        self.order_fields(self.field_order)

    def clean_first_name(self):
        first_name = self.cleaned_data['first_name']
        if first_name is None or len(first_name.strip()) <= 0:
            self.add_error('first_name', '请填写名字')
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data['last_name']
        if last_name is None or len(last_name.strip()) <= 0:
            self.add_error('last_name', '请填写姓氏')
        return last_name

    def clean_birth(self):
        return self.cleaned_data['birth']

    def clean_passport(self):
        passport = self.cleaned_data['passport']
        if passport is None or len(passport) == 0:
            self.add_error('passport', '请填写护照号码')
        return passport

    def clean_first_name_pin_yin(self):
        first_name_pin_yin = self.cleaned_data['first_name_pin_yin']
        if first_name_pin_yin is None or len(first_name_pin_yin) == 0:
            self.add_error('first_name_pin_yin', '请填写名字拼音')
        return first_name_pin_yin

    def clean_last_name_pin_yin(self):
        last_name_pin_yin = self.cleaned_data['last_name_pin_yin']
        if last_name_pin_yin is None or len(last_name_pin_yin) == 0:
            self.add_error('last_name_pin_yin', '请填写姓氏拼音')
        return last_name_pin_yin


class AppointmentInfo(forms.ModelForm):
    hospital = forms.CharField(
        label="Hospital",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False,
    )

    hospital_address = forms.CharField(
        label="Hospital Address",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False,
    )

    time = forms.DateTimeField(
        label="Appointment Time",
        widget=forms.DateTimeInput(attrs={'class': 'form-control'}),
        required=False,
    )

    name = forms.CharField(
        label="Disease Name",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False,
    )

    diagnose_hospital = forms.CharField(
        label="Hospital in China",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False,
    )

    doctor = forms.CharField(
        label="Doctor",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False,
    )

    contact = forms.CharField(
        label="Contact Info",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False,
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
        self.fields['name'].widget.attrs['readonly'] = True
        self.field_order = [
            'hospital',
            'hospital_address',
            'time',
            'name',
            'diagnose_hospital',
            'doctor',
            'contact',
        ]
        self.order_fields(self.field_order)

    def clean_diagnose_hospital(self):
        diagnose_hospital = self.cleaned_data['diagnose_hospital']
        if diagnose_hospital is None or len(diagnose_hospital.strip()) <= 0:
            self.add_error('diagnose_hospital', '请填写就诊的医院')
        return diagnose_hospital

    def clean_doctor(self):
        doctor = self.cleaned_data['doctor']
        if doctor is None or len(doctor.strip()) <= 0:
            self.add_error('doctor', '请填写就诊的医生')
        return doctor

    def clean_contact(self):
        contact = self.cleaned_data['contact']
        if contact is None or len(contact.strip()) <= 0:
            self.add_error('contact', '请填写联系人')
        return contact

    def clean(self):
        super(AppointmentInfo, self).clean()
        order = self.instance
        required, optional = get_fields(int(order.hospital.id), int(order.disease.id))
        for doc in required:
            upload = self.cleaned_data[doc]
            documents = Document.objects.filter(type=0, order=order, description=doc)
            if upload is None and len(documents) <= 0:
                self.add_error(doc, '请填写这份必要的文件')
