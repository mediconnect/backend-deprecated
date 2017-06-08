from translator.models import Translator
from supervisor.models import Supervisor
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

User.objects.create_user(username = 'translator',password = 'password',is_staff = True)
User.objects.create_user(username = 'supervisor',password = 'password', is_staff = True)

user = authenticate(username='translator',password = 'password')
translator = Translator(user)
translator.save()
user = authenticate(username='supervisor',password = 'password')
supervisor = supervisor(user)
supervisor.save()