from django import forms
from models import DynamicForm
from helper.models import Hospital, Disease


def create_form(hospital_id, disease_id, form, only_optional=False):
    hospital = Hospital.objects.get(id=hospital_id)
    disease = Disease.objects.get(id=disease_id)
    fields = DynamicForm.objects.get(hospital=hospital, disease=disease).form
    fields = [x for x in fields.split('|')]
    required, optional = (fields[0], fields[1]) if len(fields) == 2 else (fields[0], None)
    required = [x for x in required.split()]
    optional = [x for x in optional.split()]
    if not only_optional:
        for field in required:
            form.fields[field] = forms.FileField()
            form.fields[field].label = field
            form.fields[field].widget = forms.ClearableFileInput(attrs={'multiple': True})
            form.fields[field].required = True
    for field in optional:
        form.fields[field] = forms.FileField()
        form.fields[field].label = field
        form.fields[field].widget = forms.ClearableFileInput(attrs={'multiple': True})
        form.fields[field].required = False
    return form


def get_fields(hospital_id, disease_id):
    hospital = Hospital.objects.get(id=hospital_id)
    disease = Disease.objects.get(id=disease_id)
    fields = DynamicForm.objects.get(hospital=hospital, disease=disease).form
    fields = [x for x in fields.split('|')]
    required, optional = (fields[0], fields[1]) if len(fields) == 2 else (fields[0], None)
    required = [x for x in required.split()]
    optional = [x for x in optional.split()]
    return required, optional