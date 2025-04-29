from django.db import models

from werkzeug import generate_password
# Create your models here.


class User(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)
    email = models.EmailField(max_length=100, blank=False, null=False)
    password = ...