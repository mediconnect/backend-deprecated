# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-09-30 18:24
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('helper', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DynamicForm',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('form', models.CharField(default=None, max_length=150)),
                ('disease', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='dynamic_form_disease', to='helper.Disease')),
                ('hospital', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='dynamic_form_hospital', to='helper.Hospital')),
            ],
            options={
                'db_table': 'dynamic_form',
            },
        ),
    ]
