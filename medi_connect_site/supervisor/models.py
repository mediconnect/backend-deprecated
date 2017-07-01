from django.db import models
from __future__ import unicode_literals
from django.contrib.auth.models import User

class Supervisor(User):
    class Meta:
        proxy = True

    def get_name(self):
        name = self.first_name + ' ' + self.last_name
        if name is not ' ':
            return name
        return self.user.username

