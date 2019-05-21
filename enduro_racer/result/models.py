from django.db import models

# Create your models here.
from race.models.competition import Competition


class ResultsMeta(models.Model):
    resultId = models.CharField(max_length=64, primary_key=True)
    displayname = models.CharField(max_length=255)
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    valid = models.BooleanField(default=True)
    gmt_created = models.DateTimeField(auto_now_add=True)
    gmt_modified = models.DateTimeField(auto_now=True)


class RacerResults(models.Model):
    # One competition may have multiple result records,
    # such as Qualifying, or Whip, or multiple stages like EWS
    resultId = models.ForeignKey(ResultsMeta, on_delete=models.CASCADE)
    racerTag = models.CharField(max_length=16, null=True, blank=True)  # number plate
    launchTime = models.DateTimeField()
    finishTime = models.DateTimeField()
    realResult = models.TimeField()
    punishment = models.IntegerField()  # seconds, -(negative) for reward
