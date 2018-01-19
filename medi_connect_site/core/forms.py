# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError


def unique_email_validator(value):
    if User.objects.filter(email__iexact=value).exists():
        raise ValidationError('User with this Email already exists.')


class SignUpForm(forms.ModelForm):
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Confirm your password",
        required=False)
    telephone = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Telephone",
        required=False)
    address = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Address",
        required=False)

    class Meta:
        model = User
        exclude = ['last_login', 'date_joined']
        # specify fields to automatically include different inputs on website
        fields = ['email', 'password', 'first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        # specifiy the fields order on front end
        self.field_order = [
            'email',
            'password',
            'confirm_password',
            'first_name',
            'last_name',
            'telephone',
            'address',
        ]
        self.order_fields(self.field_order)
        # append validators for fields
        self.fields['email'].validators.append(unique_email_validator)
        self.fields['password'].widget = forms.PasswordInput()
        self.fields['password'].required = False
        self.fields['email'].required = False
        self.fields['first_name'].required = False
        self.fields['last_name'].required = False

    def clean(self):
        super(SignUpForm, self).clean()
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password is None or len(password) <= 0:
            self.add_error('password', '请填写密码')
        elif len(password) < 8:
            self.add_error('password', '密码长度至少是8')
        if confirm_password is None or len(confirm_password) <= 0:
            self.add_error('confirm_password', '请填写确认密码')
        if password is not None and confirm_password is not None and password != confirm_password:
            self.add_error('confirm_password', '确认密码和原密码不匹配')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email is None or len(email) <= 0:
            self.add_error('email', '请填写邮箱地址')

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if first_name is None or len(first_name) <= 0:
            self.add_error('first_name', '请填写名字')

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if last_name is None or len(last_name) <= 0:
            self.add_error('last_name', '请填写姓氏')

    def clean_telephone(self):
        telephone = self.cleaned_data.get('telephone')
        if telephone is None or len(telephone) <= 0:
            self.add_error('telephone', '请填写常用电话号码')


class LoginForm(forms.ModelForm):
    class Meta:
        model = User
        exclude = []
        fields = ['email', 'password']

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['password'].widget = forms.PasswordInput()


class SearchForm(forms.ModelForm):
    query = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=30,
        required=True,
    )

    class Meta:
        model = User
        exclude = []
        fields = []

    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)


class ContactForm(forms.ModelForm):
    message = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control'}),
        label='Message',
        required=True,
    )

    email = forms.EmailField(
        label='Email Address for Response',
    )

    class Meta:
        model = User
        exclude = []
        fields = []

    def __init__(self, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)
        self.field_order = [
            'email',
            'message',
        ]
        self.order_fields(self.field_order)


class ForgetPasswordForm(forms.ModelForm):
    email = forms.EmailField(
        label='Email Address for Response',
    )

    class Meta:
        model = User
        exclude = []
        fields = []

    def __init__(self, *args, **kwargs):
        super(ForgetPasswordForm, self).__init__(*args, **kwargs)

    def clean(self):
        super(ForgetPasswordForm, self).clean()
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password is None or len(password) <= 0:
            self.add_error('password', '请填写密码')
