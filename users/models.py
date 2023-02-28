"""Module for defining Django models related to user."""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model that extends the AbstractUser class.

    Attributes:
        is_studio_owner (bool): Indicates if the user is a studio owner.
        is_employee (bool): Indicates if the user is an employee of a studio.
        is_customer (bool): Indicates if the user is a customer of a studio.
    """
    is_studio_owner = models.BooleanField(default=False)
    is_employee = models.BooleanField(default=False)
    is_customer = models.BooleanField(default=False)
