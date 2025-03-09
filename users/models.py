from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(blank=True, null=True)  # Optional email field
    phone = models.CharField(max_length=15, unique=True)

class Contact(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contacts')

class Spam(models.Model):
    phone = models.CharField(max_length=15, unique=True)
    count = models.IntegerField(default=1)
