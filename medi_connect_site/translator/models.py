from __future__ import unicode_literals
from django.contrib.auth.models import User

Translator_C2E = 1
Translator_E2C = 2

class Translator_C2E(User):
    class Meta:
        proxy = True

    def get_name(self):
        name = self.first_name + ' ' + self.last_name
        if name is not ' ':
            return name
        return self.user.username

    def get_role(self):
        return Translator_C2E



class Translator_E2C(User):
    class Meta:
        proxy = True

    def get_name(self):
        name = self.first_name + ' ' +self.last_name
        if name is not ' ':
            return name
        return self.user.username

    def get_role(self):
        return Translator_E2C