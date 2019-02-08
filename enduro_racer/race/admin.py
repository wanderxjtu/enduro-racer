from django.contrib import admin
from race.models.competition import Competition, Serials
from race.models.racer import RacerInfo, RacerLog, RacerResults, Team
from race.models.user import User, Oauth
from race.models.config import Config

# Register your models here.
admin.site.register(Competition)
admin.site.register(Serials)
admin.site.register(RacerInfo)
admin.site.register(RacerLog)
admin.site.register(RacerResults)
admin.site.register(Team)
admin.site.register(User)
admin.site.register(Oauth)
admin.site.register(Config)
