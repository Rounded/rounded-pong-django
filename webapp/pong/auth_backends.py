from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import check_password

User = get_user_model()


class EmailBackend(object):
    """
    Authenticate against Email and Password for a user
    """

    def authenticate(self, username=None, password=None):
        try:
            user = User.objects.get(email=username)
            if user.check_password(password):
                return user
            else:
                return None
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

