from django import forms
from django.contrib.auth.models import User
from helper.models import Patient, Document, Order
from customer.models import Customer


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="First Name",
        required=True)

    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Last Name",
        required=True)

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        label="Email",
        required=True)

    class Meta:
        model = Customer
        exclude = []
        fields = ['address', 'tel', 'wechat']

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.field_order = [
            'first_name',
            'last_name',
            'email',
            'address',
            'tel',
            'wechat'
        ]
        self.order_fields(self.field_order)


class PasswordResetForm(forms.ModelForm):
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Confirm your password",
        required=True)

    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Enter your old password",
        required=True)

    class Meta:
        model = User
        exclude = []
        fields = ['password']

    def __init__(self, *args, **kwargs):
        super(PasswordResetForm, self).__init__(*args, **kwargs)
        self.field_order = [
            'old_password',
            'password',
            'confirm_password'
        ]
        self.order_fields(self.field_order)
        self.fields['password'].widget = forms.PasswordInput()
        self.fields['password'].required = True

    def clean(self):
        super(PasswordResetForm, self).clean()
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password and password != confirm_password:
            self._errors['password'] = self.error_class(
                ['Passwords don\'t match']
            )
            self._errors['confirm_password'] = self.error_class(
                ['Passwords don\'t match']
            )
        return self.cleaned_data


class PatientAddForm(forms.ModelForm):
    class Meta:
        model = Patient
        exclude = []
        fields = ['first_name', 'last_name', 'birth', 'gender', 'pin_yin']

    def __init__(self, *args, **kwargs):
        super(PatientAddForm, self).__init__(*args, **kwargs)
        self.fields['birth'].widget = forms.DateInput(attrs={'class': 'datepicker'})


class DocAddForm(forms.ModelForm):
    class Meta:
        model = Document
        exclude = []
        fields = []

    def __init__(self, *args, **kwargs):
        super(DocAddForm, self).__init__(*args, **kwargs)

class PayRemainingForm(forms.Form):
    remaining_amount = forms.IntegerField(
        label = 'The remaining amount is: ',
        disabled= True
    )