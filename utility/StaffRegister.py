from helper.models import Staff
from django.contrib.auth.models import User
role_accept = '12'
finished = False
email_checked = False
def check_email(s):
    if '@' not in s:
        return False
    return True

while(not finished):
    while True:
        role=raw_input('Do you want to register for a translator or supervisor? (Enter 1 for translator, 2 for supervisor)')
        if role in role_accept:
            break
        print('Not valid, try again')
    email = raw_input('Please enter an email:')
    pwd = raw_input('Please enter a password:')
    user = User.objects.create_user(username=email,email=email,password=pwd)
    if role == 1:
        while True:
            trans_role = raw_input(
                'Do you want to register for a C2E or E2C? (Enter 1 for C2E, 2 for E2C)')
            if role in role_accept:
                break
            print('Not valid, try again')
        user.save()
        if trans_role == 1:
            C2E = Staff(user = user, role= 1,is_staff=1)
            C2E.save()
            print('Succeed')
        if trans_role == 2:
            E2C = Staff(user = user, role = 2,is_staff=1)
            E2C.save()
            print('Succeed')
    if role == 2:
        user.save()
        supervisor = Staff(user = user, role = 0,is_staff=1)
        supervisor.save()
        print('Succeed')
    while True:
        f=raw_input('Do you want to create another staff? Y/N' )
        if f is 'N' or f is 'n':
            finished = True
            break
        if f is 'Y' or f is 'y':
            break
        print('Not valid')

