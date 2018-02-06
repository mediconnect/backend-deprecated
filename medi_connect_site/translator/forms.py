# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from helper.models import Document, Order
import info.utility as util

class AssignmentSummaryForm(forms.ModelForm):
	class Meta:
		model = Document
		fields = ['document']

class StaffLoginForm(forms.ModelForm):
    class Meta:
        model = User
        exclude = []
        fields = ['email', 'password']

    def __init__(self, *args, **kwargs):
        super(StaffLoginForm, self).__init__(*args, **kwargs)
        self.fields['password'].widget = forms.PasswordInput()

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