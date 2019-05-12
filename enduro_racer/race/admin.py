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
import csv

from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path

from race.models.competition import Competition, Serials
from race.models.racer import RacerInfo, RacerLog, RacerResults, Team
from race.models.user import User, Oauth
from race.models.config import Config


class RacerInfoAdmin(admin.ModelAdmin):
    list_display = ("realName", "gender", "birthday")
    search_fields = ("realName",)


class RacerLogAdmin(admin.ModelAdmin):
    list_display = ("racerId", "teamId", "group", "competitionId")
    list_filter = ("competitionId", "group")
    search_fields = ("racerId",)
    change_list_template = "racerlog_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import-csv/', self.import_csv),
        ]
        return my_urls + urls

    def import_csv(self, request):
        if request.method == "POST":
            csv_file = request.FILES["csv_file"]
            reader = csv.reader(csv_file)
            for row in reader:
                # TODO: parsing Racer Signup Info csv file
                # TODO: realName, gender, birthday, competitionName, teamName, group?
                pass

            self.message_user(request, "Your csv file has been imported")
            return redirect("..")


# Register your models here.
admin.site.register(Competition)
admin.site.register(Serials)
admin.site.register(RacerInfo, RacerInfoAdmin)
admin.site.register(RacerLog, RacerLogAdmin)
admin.site.register(RacerResults)
admin.site.register(Team)
admin.site.register(User)
admin.site.register(Oauth)
admin.site.register(Config)
