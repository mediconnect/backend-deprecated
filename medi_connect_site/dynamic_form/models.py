# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from helper.models import Hospital, Disease


# Create your models here.
class DynamicForm(models.Model):
    hospital = models.ForeignKey(Hospital, unique=False, default=None, related_name='dynamic_form_hospital')
    disease = models.ForeignKey(Disease, unique=False, default=None, related_name='dynamic_form_disease')
    form = models.CharField(default=None, max_length=150)

    class Meta:
        db_table = 'dynamic_form'
