# coding=utf-8
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
    age = models.SmallIntegerField()
    region = models.CharField(max_length=4, default="CHN")  # iso code, default
    idType = models.SmallIntegerField(choices=[(s.value, s) for s in IdType],
                                      default=IdType.Identity.value)
    idNumber = models.CharField(max_length=255)  # id number or passport number
    phoneNumber = models.CharField(max_length=32)

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
