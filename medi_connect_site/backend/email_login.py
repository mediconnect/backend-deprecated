from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class EmailLoginBackend(ModelBackend):
    def authenticate(self, email=None, password=None, **kwargs):
        usermodel = get_user_model()
        try:
            user = usermodel.objects.get(email=email)
        except usermodel.DoesNotExist:
            return None
        else:
            if getattr(user, 'is_active', False) and user.check_password(password):
                return user
        return None
