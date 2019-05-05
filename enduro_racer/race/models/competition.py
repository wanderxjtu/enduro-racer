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


class CompStatus(Enum):
    Pending = 0  # 即将开始报名
    Signing = 1  # 报名中
    StopSign = 2  # 停止自助报名


class Serials(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(max_length=65535)
    gmt_created = models.DateTimeField(auto_now_add=True)
    gmt_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Competition(models.Model):
    name = models.CharField(max_length=255)
    uniname = models.CharField(max_length=64, unique=True)  # designed for url path, generated automatically
    description = models.TextField(max_length=65535)
    groupSetting = models.CharField(max_length=255)  # csv format
    manager = models.CharField(max_length=255)
    serialId = models.ForeignKey(Serials, on_delete=models.DO_NOTHING)
    startDate = models.DateField()
    endDate = models.DateField()
    location = models.CharField(max_length=255)

    signUpOpen = models.BooleanField(default=False)
    signUpStartDate = models.DateTimeField()
    signUpEndDate = models.DateTimeField()
    signUpFee = models.IntegerField()
    maxRacerCount = models.IntegerField()
    CompetitionStatus = models.SmallIntegerField(choices=[(s.value, s) for s in CompStatus],
                                                 default=CompStatus.Pending.value)  # see CompStatus
    resultConfig = models.TextField(max_length=65535)
    gmt_created = models.DateTimeField(auto_now_add=True)
    gmt_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.uniname
