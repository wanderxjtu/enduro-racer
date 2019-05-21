from django.contrib import admin

# Register your models here.
from result.models import RacerResults, ResultsMeta

admin.site.register(RacerResults)
admin.site.register(ResultsMeta)
