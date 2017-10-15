# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-10-15 02:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('helper', '0002_auto_20171014_2103'),
    ]

    operations = [
        migrations.RenameField(
            model_name='orderpatient',
            old_name='name',
            new_name='first_name',
        ),
        migrations.RenameField(
            model_name='patient',
            old_name='name',
            new_name='first_name',
        ),
        migrations.AddField(
            model_name='orderpatient',
            name='last_name',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AddField(
            model_name='patient',
            name='last_name',
            field=models.CharField(default='', max_length=50),
        ),
    ]
