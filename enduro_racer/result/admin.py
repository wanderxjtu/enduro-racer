from django.contrib import admin

# Register your models here.
from django.http import HttpResponseRedirect
from django.shortcuts import render

from race.models import Config
from result.models import RacerResults, ResultsMeta
from result.read_result_raw_bb import BBRawResultReader


def load_result_view(self, request, form_url='', extra_context=None):
    try:
        ongoing_uniname = Config.objects.get(key="LoadingCompetition").value
    except:
        ongoing_uniname = None
    if not ongoing_uniname:
        self.message_user(request, "加载记录失败，当前没有进行中的比赛", 30)
    else:
        BBRawResultReader().read_result(ongoing_uniname)
        self.message_user(request, "加载了 %s 比赛记录" % ongoing_uniname)
    return HttpResponseRedirect("../")


class ResultsAdmin(admin.ModelAdmin):
    list_display = ("get_result_id", "get_result_displayname", "racerTag", "get_realResult_str")
    list_filter = ("resultId__displayname", "racerTag")
    readonly_fields = ("resultId", "launchTime", "finishTime", "realResult", "punishment",)

    def get_result_id(self, obj):
        return obj.resultId.resultId

    def get_result_displayname(self, obj):
        return obj.resultId.displayname

    def get_realResult_str(self, obj):
        return obj.realResult.strftime("%H:%M:%S.%f")[:-3]

    add_view = load_result_view


class ResultMetaAdmin(admin.ModelAdmin):
    list_display = ("resultId", "belongs_to_comp", "displayname", "valid")
    list_filter = ("competition__uniname",)
    readonly_fields = ("resultId",)
    actions = ("make_valid",)  # "make_invalid")

    def belongs_to_comp(self, obj):
        return obj.competition.uniname

    def make_valid(self, request, queryset):
        for obj in queryset:
            obj.valid = True
            obj.save()

    def make_invalid(self, request, queryset):
        for obj in queryset:
            obj.valid = False
            obj.save()

    add_view = load_result_view

    make_valid.short_description = "设置为有效成绩单"
    make_invalid.short_description = "设置为无效成绩单"


admin.site.register(RacerResults, ResultsAdmin)
admin.site.register(ResultsMeta, ResultMetaAdmin)
