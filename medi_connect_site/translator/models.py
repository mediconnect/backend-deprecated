from django.contrib.auth.models import User
from django.db import models

#Create your models here.
ACTIVE = True
INACTIVE = False

class Translator(models.Model):
	user = models.OneToOneField(User)

	class Meta:
		db_table = 'auth_translator'
		
	def get_name(self):
		return '111'