# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-08-15 01:45
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('helper', '0007_auto_20170813_2256'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='submit',
            field=models.DateTimeField(default=datetime.datetime(2017, 8, 15, 1, 45, 17, 144441, tzinfo=utc)),
        ),
    ]
