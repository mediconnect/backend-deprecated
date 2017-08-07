# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-08-02 19:46
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('helper', '0004_auto_20170731_1257'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='step',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='submit',
            field=models.DateTimeField(default=datetime.datetime(2017, 8, 2, 19, 46, 40, 962000, tzinfo=utc)),
        ),
    ]
