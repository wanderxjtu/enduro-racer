from django.contrib import admin

# Register your models here.
from result.models import RacerResults, ResultsMeta


class ResultsAdmin(admin.ModelAdmin):
    list_display = ("get_result_id", "get_result_displayname", "racerTag", "get_realResult_str")
    readonly_fields = ("racerTag", "launchTime", "finishTime", "realResult", "punishment",)

    def get_result_id(self, obj):
        return obj.resultId.resultId

    def get_result_displayname(self, obj):
        return obj.resultId.displayname

    def get_realResult_str(self, obj):
        return obj.realResult.strftime("%H:%M:%S.%f")[:-3]


class ResultMetaAdmin(admin.ModelAdmin):
    list_display = ("resultId", "belongs_to_comp", "displayname", "valid")
    readonly_fields = ("resultId",)

    def belongs_to_comp(self, obj):
        return obj.competition.uniname


admin.site.register(RacerResults, ResultsAdmin)
admin.site.register(ResultsMeta, ResultMetaAdmin)
