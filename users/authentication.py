from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class EmailBackend(BaseBackend):
    """A backend that authenticates users."""
    def authenticate(self, request, username=None, password=None, **kwargs):
        """Authenticates user by email and password.

        Args:
            request (HttpRequest): The current request.
            username (str): The email address of the user.
            password (str): The password of the user.
            kwargs: Any additional arguments passed to the method.
        Returns:
            user (User): The authenticated user if email and password are correct, None otherwise.
        """
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None

        if user.check_password(password):
            return user

    def get_user(self, user_id):
        """Retrieves the user instance by user ID.

        Args:
            user_id (int): The ID of the user to retrieve.

        Returns:
            user (User): The user instance if it exists, None otherwise.
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
