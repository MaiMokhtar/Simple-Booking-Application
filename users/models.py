from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    is_studio_owner = models.BooleanField(default=False)
    is_employee = models.BooleanField(default=False)
    is_customer = models.BooleanField(default=False)
