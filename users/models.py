from django.contrib.auth.models import AbstractUser
from django.db import models

USER_TYPES = (
    ('studio_owner', 'Studio Owner'),
    ('employee', 'Employee'),
    ('customer', 'Customer'),
)


class User(AbstractUser):
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='customer')
    is_studio_owner = models.BooleanField(default=False)
    is_employee = models.BooleanField(default=False)
    is_customer = models.BooleanField(default=False)
