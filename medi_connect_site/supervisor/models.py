
from django.contrib.auth.models import User
from django.db import models

class Supervisor(models.Model):
	user = models.OneToOneField(User)

	class Meta:
		db_table = 'auth_supervisor'