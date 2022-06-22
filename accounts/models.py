from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

"""
CustomUser: A placeholder for a user to login/logout/signup.
Can connect with other models with OneToOneFields for further implementation of other types of users.
"""

class CustomUser(AbstractUser):
    pass

    def __str__(self):
        return self.username

