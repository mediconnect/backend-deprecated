# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.models import User
from helper.models import Document, Order, Staff, Questionnaire
from django.core.exceptions import ValidationError
import info.utility as util

C2E_assignee_choice = []
for e in Staff.objects.filter(role = 1):
    C2E_assignee_choice.append((e.user.id,e.get_name()))

E2C_assignee_choice = []
for e in Staff.objects.filter(role = 2):
    E2C_assignee_choice.append((e.user.id,e.get_name()))

class C2E_AssignForm(forms.ModelForm):
    assignee = forms.ChoiceField(choices=C2E_assignee_choice)
    class Meta:
        model = Order
        fields = ['assignee']

class E2C_AssignForm(forms.ModelForm):
    E2C_new_assignee = forms.ChoiceField(choices=E2C_assignee_choice)

    class Meta:
        model = Order
        fields = ['E2C_new_assignee']

class ApproveForm(forms.ModelForm):
    approval = forms.TypedChoiceField(
        coerce=lambda x: x == 'True',
        choices=((False, 'DISAPPROVE'), (True, 'APRROVE')),
        widget=forms.RadioSelect,
        required=True
    )
    class Meta:
        model = Order
        fields = ['approval']

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






def forbidden_username_validator(value):
    forbidden_username = ['admin', 'settings', 'news', 'about', 'help',
                          'signin', 'signup', 'signout', 'terms', 'privacy',
                          'cookie', 'new', 'login', 'logout', 'administrator',
                          'join', 'account', 'username', 'root', 'blog',
                          'user', 'users', 'billing', 'subscribe', 'reviews',
                          'review', 'blog', 'blogs', 'edit', 'mail', 'email',
                          'core', 'job', 'jobs', 'contribute', 'newsletter',
                          'shop', 'profile', 'register', 'auth',
                          'authentication', 'campaign', 'config', 'delete',
                          'remove', 'forum', 'forums', 'download',
                          'downloads', 'contact', 'blogs', 'feed', 'feeds',
                          'faq', 'intranet', 'log', 'registration', 'search',
                          'explore', 'rss', 'support', 'status', 'static',
                          'media', 'setting', 'css', 'js', 'follow',
                          'activity', 'questions', 'articles', 'network', ]

    if value.lower() in forbidden_username:
        raise ValidationError('This is a reserved word.')


def invalid_username_validator(value):
    if '@' in value or '+' in value or '-' in value:
        raise ValidationError('Enter a valid username.')


def unique_email_validator(value):
    if User.objects.filter(email__iexact=value).exists():
        raise ValidationError('User with this Email already exists.')


def unique_username_ignore_case_validator(value):
    if User.objects.filter(username__iexact=value).exists():
        raise ValidationError('User with this Username already exists.')

ROLE_CHOICES = (
    (1,'Translator_C2E'),
    (2,'Translator_E2C')
)
class TransSignUpForm(forms.ModelForm):
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(),
        label="Confirm your password",
        required=True)

    role = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=ROLE_CHOICES,
        required=True)

    class Meta:
        model = User
        exclude = ['last_login', 'date_joined']
        # specify fields to automatically include different inputs on website
        fields = ['email', 'password', 'first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        super(TransSignUpForm, self).__init__(*args, **kwargs)
        # specifiy the fields order on front end
        self.field_order = [
            'email',
            'password',
            'confirm_password',
            'first_name',
            'last_name',
            'role'
        ]
        self.order_fields(self.field_order)
        # append validators for fields
        self.fields['email'].validators.append(unique_email_validator)
        self.fields['password'].widget = forms.PasswordInput()
        self.fields['password'].required = True
        self.fields['email'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['role'].required = True

    def clean(self):
        """
        the clean function is automatically called by Django framework during upon
        data transformation to back end. developers can use it to append error, and
        check the validity of user input.
        """
        super(TransSignUpForm, self).clean()
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


class GenerateQuestionnaireForm(forms.Form):
    question=forms.CharField(
        label='问题内容:',
        required=True
    )
    format=forms.ChoiceField(
        label='问题形式:',
        widget=forms.RadioSelect,
        choices=util.FORMAT_CHOICE,
        required=True
    )

class ChoiceForm(forms.Form):
    choice = forms.CharField(
        label = '选项内容:',
        widget=forms.TextInput,
        required=True
    )