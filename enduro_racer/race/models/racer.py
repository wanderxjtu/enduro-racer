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
from .competition import Competition


class Gender(Enum):
    Female = 0
    Male = 1


class IdType(Enum):
    Identity = 0
    Passport = 1


class RacerStatus(Enum):
    WaitForPayment = 0
    DoNotStart = 1
    DoNotFinish = 2
    Finished = 3
    Foul = 4


class Team(models.Model):
    name = models.CharField(max_length=255)
    leaderName = models.CharField(max_length=255)
    leaderPhone = models.CharField(max_length=32)

    def __str__(self):
        return self.name


class RacerInfo(models.Model):
    # racer signup infomation
    realName = models.CharField(max_length=255)
    gender = models.SmallIntegerField(choices=[(s.value, s) for s in Gender])
    # age = models.SmallIntegerField()  # this should be calculate by birthday
    birthday = models.DateField()
    region = models.CharField(max_length=4, default="CHN")  # iso code, default
    idType = models.SmallIntegerField(choices=[(s.value, s) for s in IdType],
                                      default=IdType.Identity.value)
    idNumber = models.CharField(max_length=255, unique=True)  # id number or passport number
    phoneNumber = models.CharField(max_length=32)

    ecpName = models.CharField(max_length=255, null=True, blank=True)  # emergency contact person
    ecpNumber = models.CharField(max_length=32, null=True, blank=True)  # emergency contact phone

    def __str__(self):
        return self.realName


class RacerLog(models.Model):
    racerId = models.ForeignKey(RacerInfo, on_delete=models.DO_NOTHING)  # racer identifier, pointed to racerinfo
    competitionId = models.ForeignKey(Competition, on_delete=models.DO_NOTHING)  # competition
    teamId = models.ForeignKey(Team, on_delete=models.DO_NOTHING)  # pointed to team
    group = models.CharField(max_length=32)
    racerTag = models.CharField(max_length=16)  # number plate
    status = models.SmallIntegerField(choices=[(s.value, s) for s in RacerStatus],
                                      default=RacerStatus.WaitForPayment.value)
    rank = models.SmallIntegerField(null=True, blank=True)
    points = models.SmallIntegerField(null=True, blank=True)

    def __str__(self):
        return self.competitionId.uniname + "," + self.racerTag + "," + self.racerId.realName


class RacerResults(models.Model):
    # One competition may have multiple result records,
    # such as Qualifying, or Whip, or multiple segment like EWS
    racerLogId = models.ForeignKey(RacerLog, on_delete=models.DO_NOTHING)
    launchTime = models.DateTimeField()
    finishTime = models.DateTimeField()
    punishment = models.IntegerField()  # seconds, -(negative) for reward

    def __str__(self):
        return self.racerLogId.racerId.realName
