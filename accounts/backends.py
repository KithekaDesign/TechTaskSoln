from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class EmailBackend(ModelBackend):
    """
    Custom authentication backend that authenticates users by email
    instead of username. Required because SimpleJWT's token serializer
    calls Django's authenticate() internally.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        # SimpleJWT passes the credential as `username` regardless of
        # the serializer's username_field setting, so we look it up as email.
        email = username or kwargs.get('email')
        if email is None:
            return None

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
