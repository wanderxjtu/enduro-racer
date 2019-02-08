from django.db import models


class Config(models.Model):
    key = models.CharField(max_length=255)
    value = models.CharField(max_length=4096)
