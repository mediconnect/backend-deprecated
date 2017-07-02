# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-02 02:37
from __future__ import unicode_literals

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import helper.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('customer', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('week_1', models.PositiveSmallIntegerField(default=0)),
                ('week_2', models.PositiveSmallIntegerField(default=0)),
                ('week_3', models.PositiveSmallIntegerField(default=0)),
                ('week_4', models.PositiveSmallIntegerField(default=0)),
            ],
            options={
                'db_table': 'appointment',
            },
        ),
        migrations.CreateModel(
            name='Disease',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='unknown', max_length=50)),
                ('keyword', models.CharField(default='unknown', max_length=150)),
            ],
            options={
                'db_table': 'disease',
            },
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(blank=True, max_length=50)),
                ('required', models.BooleanField(default=False)),
                ('is_origin', models.BooleanField(default=True)),
                ('is_translated', models.BooleanField(default=False)),
                ('upload_at', models.DateTimeField(auto_now_add=True)),
                ('comment', models.CharField(blank=True, max_length=255)),
                ('document', models.FileField(null=True, upload_to=helper.models.order_directory_path)),
            ],
            options={
                'db_table': 'document',
            },
        ),
        migrations.CreateModel(
            name='Hospital',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('area', models.CharField(blank=True, max_length=50)),
                ('slots_open', models.IntegerField(default=20)),
                ('overall_rank', models.IntegerField(default=0)),
                ('website', models.URLField(blank=True)),
                ('introduction', models.TextField(default='intro')),
                ('specialty', models.TextField(default='specialty')),
                ('feedback_time', models.CharField(default='one week', max_length=50)),
                ('price_range', models.CharField(default='unknown', max_length=50)),
            ],
            options={
                'db_table': 'hospital',
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('submit', models.DateField(default=datetime.date.today)),
                ('receive', models.DateField(default=datetime.date.today)),
                ('status', models.CharField(blank=True, choices=[(0, 'started'), (1, 'submitted'), (2, 'translating_origin'), (3, 'received'), (4, 'return'), (5, 'translating_feedback'), (6, 'feedback'), (7, 'PAID')], max_length=20)),
                ('trans_status', models.CharField(blank=True, choices=[(0, 'not_started'), (1, 'ongoing'), (2, 'approving'), (3, 'approved'), (4, 'disapproved'), (5, 'finished')], max_length=20)),
                ('customer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='customer.Customer')),
                ('disease', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='helper.Disease')),
                ('feedback', models.ManyToManyField(related_name='feedback_file', to='helper.Document')),
                ('hospital', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='helper.Hospital')),
                ('origin', models.ManyToManyField(related_name='original_file', to='helper.Document')),
            ],
            options={
                'db_table': 'order',
            },
        ),
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=50)),
                ('age', models.IntegerField(blank=True)),
                ('gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female'), ('OTHER', 'Other')], default='M', max_length=5)),
                ('category', models.CharField(default='COLD', max_length=50)),
                ('diagnose_hospital', models.CharField(blank=True, max_length=50)),
                ('doctor', models.TextField(blank=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='customer.Customer')),
            ],
            options={
                'db_table': 'patient',
            },
        ),
        migrations.CreateModel(
            name='Rank',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rank', models.IntegerField(default=0)),
                ('disease', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='helper.Disease')),
                ('hospital', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='helper.Hospital')),
            ],
            options={
                'db_table': 'rank',
            },
        ),
        migrations.AddField(
            model_name='order',
            name='patient',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='helper.Patient'),
        ),
        migrations.AddField(
            model_name='order',
            name='pending',
            field=models.ManyToManyField(related_name='pending_file', to='helper.Document'),
        ),
        migrations.AddField(
            model_name='order',
            name='translator_C2E',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='chinese_translator', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='order',
            name='translator_E2C',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='english_translator', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='document',
            name='order',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='helper.Order'),
        ),
        migrations.AddField(
            model_name='appointment',
            name='hospital',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='helper.Hospital'),
        ),
    ]
