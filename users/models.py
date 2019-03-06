from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class User(AbstractUser):
    security_key = models.CharField(max_length=40, null=True, blank=True)
    security_key_expires = models.DateTimeField(null=True, blank=True)
