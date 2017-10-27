# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-26 16:27
from __future__ import unicode_literals

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('wechat', models.CharField(blank=True, max_length=50)),
                ('weibo', models.CharField(blank=True, max_length=50)),
                ('qq', models.CharField(blank=True, max_length=50)),
                ('tel', models.CharField(default=b'unknown', max_length=50)),
                ('address', models.CharField(blank=True, max_length=50)),
                ('zipcode', models.CharField(default=b'unknown', max_length=50)),
                ('register_time', models.DateField(default=datetime.date.today)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'auth_customer',
            },
        ),
    ]
