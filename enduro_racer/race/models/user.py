# coding=utf-8
"""
    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
   ------------------------------------------------------
   File Name : ${NAME}
   Author : jiaqi.hjq
"""
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
