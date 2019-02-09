from enum import Enum

from django.db import models


class CompStatus(Enum):
    Pending = 0  # 即将开始报名
    Signing = 1  # 报名中
    StopSign = 2  # 停止自助报名


class Serials(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(max_length=65535)

    def __str__(self):
        return self.name


class Competition(models.Model):
    name = models.CharField(max_length=255)
    uniname = models.CharField(max_length=1024)  # designed for url path, generated automatically
    description = models.TextField(max_length=65535)
    groupSetting = models.CharField(max_length=255)  # csv format
    serialId = models.ForeignKey(Serials, on_delete=models.DO_NOTHING)
    startDate = models.DateField()
    endDate = models.DateField()
    location = models.CharField(max_length=255)

    signUpOpen = models.BooleanField(default=False)
    signUpStartDate = models.DateTimeField()
    signUpEndDate = models.DateTimeField()
    signUpFee = models.IntegerField()
    CompetitionStatus = models.SmallIntegerField(choices=[(s.value, s) for s in CompStatus],
                                                 default=CompStatus.Pending.value)  # see CompStatus

    def __str__(self):
        return self.uniname
