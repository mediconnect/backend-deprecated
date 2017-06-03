# from __future__ import unicode_literals
# from django.contrib.auth.models import User
# from helper.models import Document
# from django.db import models
#
# # Create your models here.
# ACTIVE = True
# INACTIVE = False
#
# class Translator(models.Model):
# 	user = models.OneToOneField(User)
# 	email = models.EmailFiled(default = 'unknown')
# 	status = models.BooleanField(default = INACTIVE)
# 	supervisor = models.ForienKey(Supervisor)
#
# class Supervisor(models.Model):
# 	user = models.OneToOneField(User)