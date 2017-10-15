from django import forms
from django.core.exceptions import ValidationError

from helper.models import Order, Patient


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
        fields = ['name', 'birth', 'gender', 'relationship', 'passport']

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
        self.field_order = [
            'contact', 'email', 'address', 'telephone', 'wechat', 'qq', 'first_name_pin_yin', 'last_name_pin_yin'
        ]
        self.order_fields(self.field_order)

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

    name = forms.CharField(
        label="Disease Name",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True,
    )

    diagnose_hospital = forms.CharField(
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
