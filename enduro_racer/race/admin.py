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
