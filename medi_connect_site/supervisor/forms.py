from django import forms
from django.contrib.auth.models import User
from helper.models import Document, Order
from translator.models import Translator
import random

assignee_choice = []
for e in Translator.objects.filter(is_staff = 1):
    assignee_choice.append((e,e.get_name()))

class DetailForm(forms.ModelForm):
    approval = forms.TypedChoiceField(
        coerce=lambda x: x == 'True',
        choices=((False, 'DISAPPROVE'), (True, 'APRROVE')),
        widget=forms.RadioSelect,
        required= False
    )
    new_assignee = forms.ChoiceField(choices = assignee_choice,required= False)
    feedback_documents = forms.FileField(required= False)
    class Meta:
        model = Order
        fields = ['new_assignee','approval','feedback_documents']

class ResetPasswordForm(forms.Form):
    password = forms.PasswordInput()

class FeedbackUploadForm(forms.Form):
    file_field = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))


class TransSignUpForm(forms.ModelForm):
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Confirm your password",
        required=True)

    class Meta:
        model = User
        exclude = ['last_login', 'date_joined']
        fields = ['username', 'email', 'password', 'first_name', 'last_name']
        
	def __init__(self, *args, **kwargs):
		
		super(TransSignUpForm, self).__init__(*args, **kwargs)
		self.field_order = ['username','password','confirm_password','first_name','last_name','email']
		self.order_fields(self.field_order)
		self.fields['password'].widget = forms.PasswordInput(attrs={'class': 'form-control'},required = True)

    def clean(self):
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
