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
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import path
from django.utils.html import format_html

from race.models import Competition, Serials, RacerInfo, RacerLog, Team, Config


class RacerInfoAdmin(admin.ModelAdmin):
    list_display = ("realName", "gender", "birthday")
    search_fields = ("realName",)


class CompetitionAdmin(admin.ModelAdmin):
    list_display = ("uniname", "name", "signUpOpen", "serialId", "ongoing", "import_racers", "racers_info")
    actions = ("make_ongoing",)

    def make_ongoing(self, request, queryset):
        obj = queryset[0]
        try:
            Config.objects.filter(key="LoadingCompetition").update(value=obj.uniname)
        except:
            Config(key="LoadingCompetition", value=obj.uniname).save()

    make_ongoing.short_description = "设置为比赛中"

    def import_racers(self, obj):
        return format_html('<a href="{0.id}/import-racers/">导入参赛名单</a>'.format(obj))

    import_racers.short_description = "导入"

    def racers_info(self, obj):
        return format_html('<a href="{0.uniname}/export-racers/">{0.uniname}.csv</a>'.format(obj))

    racers_info.short_description = "导出"

    def ongoing(self, obj):
        if obj.uniname == Config.objects.get(key="LoadingCompetition").value:
            return "比赛中"
        return ""

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('<path:object_uniname>/export-racers/', self.export_csv),
            path('<path:object_id>/import-racers/', self.import_csv)
        ]
        return my_urls + urls

    def export_csv(self, request, object_uniname, extra_context=None):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(object_uniname)
        writer = csv.writer(response)
        # TODO: write
        return response

    def import_csv(self, request, object_id, *args, **kwargs):
        if request.method == "POST":
            csv_file = request.FILES["csv_file"]
            reader = csv.reader(csv_file)
            for row in reader:
                # TODO: parsing Racer Signup Info csv file
                # TODO: comp_uniname, realName, gender, birthday, teamName, group?
                pass

            self.message_user(request, "Your csv file has been imported")
            return redirect("../../")
        return render(request, "csv_import.html", {"title": "导入参赛名单", "site_header": self.admin_site.site_header})


class RacerLogAdmin(admin.ModelAdmin):
    list_display = ("racerId", "teamId", "group", "competitionId")
    list_filter = ("competitionId", "group")
    readonly_fields = ("competitionId", "racerId")
    search_fields = ("racerId",)


class ConfigAdmin(admin.ModelAdmin):
    list_display = ("key", "value")
    readonly_fields = ("key",)


class TeamAdmin(admin.ModelAdmin):
    list_display = ("name", "leaderName")


# Register your models here.
admin.site.register(Competition, CompetitionAdmin)
admin.site.register(Serials)
admin.site.register(RacerInfo, RacerInfoAdmin)
admin.site.register(RacerLog, RacerLogAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Config, ConfigAdmin)
