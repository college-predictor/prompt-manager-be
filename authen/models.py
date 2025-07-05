from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, email, **extra_fields):
        if not email:
            raise ValueError("The email must be set")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_unusable_password()
        user.save()
        return user


class User(AbstractUser):
    username = None
    name = models.TextField(null=False)
    email = models.EmailField(unique=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = UserManager()

    def __str__(self):
        return self.email