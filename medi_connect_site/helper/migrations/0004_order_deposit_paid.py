# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-09-17 14:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('helper', '0003_remove_hospitalreview_review_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='deposit_paid',
            field=models.BooleanField(default=False),
        ),
    ]
