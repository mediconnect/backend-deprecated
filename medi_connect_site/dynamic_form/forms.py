from django import forms
from models import DynamicForm
from helper.models import Hospital, Disease


def create_form(hospital_id, disease_id, form):
    hospital = Hospital.objects.get(id=hospital_id)
    disease = Disease.objects.get(id=disease_id)
    required = DynamicForm.objects.get(hospital=hospital, disease=disease).form
    for field in required.split():
        form.fields[field] = forms.FileField()
        form.fields[field].label = field
        form.fields[field].widget = forms.ClearableFileInput(attrs={'multiple': True})
        form.fields[field].requried = True
    return form


def get_fields(hospital_id, disease_id):
    hospital = Hospital.objects.get(id=hospital_id)
    disease = Disease.objects.get(id=disease_id)
    required = DynamicForm.objects.get(hospital=hospital, disease=disease).form
    fields = [x for x in required.split()]
    return fields