from enum import Enum

from django.db import models

# Create your models here.
from .racer import RacerInfo


class Role(Enum):
    Root = 0
    Admin = 1
    RaceAdmin = 2
    NormalUser = 100


class User(models.Model):
    displayname = models.CharField(max_length=255)  # displayname
    loginname = models.CharField(max_length=255)  # displayname
    password = models.CharField(max_length=255)  # reserve
    racer = models.ForeignKey(RacerInfo, on_delete=models.SET_NULL, null=True, blank=True)
    role = models.IntegerField(choices=[(s.value, s) for s in Role], default=Role.NormalUser.value)  # pointed to role

    def __str__(self):
        return self.displayname


class Oauth(models.Model):
    oauthtype = models.CharField(max_length=255)
    oauthname = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.displayname
