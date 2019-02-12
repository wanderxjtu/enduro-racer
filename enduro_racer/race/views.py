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
import logging

from race.models.racer import RacerLog

LOGGER = logging.getLogger(__file__)
from datetime import datetime

from django.db.models import QuerySet, Model
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

# Create your views here.
from django.views.generic import TemplateView
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView

from .models.competition import Competition


class IndexView(TemplateView):
    template_name = "index.html"


class JsonViewMixin:
    def render_to_response(self, context, **response_kwargs):
        obj = context['object']
        return JsonResponse({'object': obj}, **response_kwargs)


class JsonListViewMixin:
    def render_to_response(self, context, **response_kwargs):
        objname = self.get_context_object_name(context["object_list"])
        objs = context[objname]

        return JsonResponse({objname: list(objs)}, **response_kwargs)


class CompetitionListView(JsonListViewMixin, BaseListView):
    context_object_name = 'competitions'
    ordering = ["-startDate", "-endDate"]

    def get_queryset(self):
        qs = Competition.objects.select_related('serialId')
        qs = qs.filter(signUpOpen=True) if self.request.GET.get("showOpen", False) == "true" else qs.all()
        return qs.values()


class CompetitionGroupListView(JsonListViewMixin, BaseListView):
    context_object_name = 'groups'

    def get_queryset(self):
        # obj = get_object_or_404(Competition, uniname=self.kwargs['competition_uniname'])
        return RacerLog.objects.select_related('competitionId__uniname', 'racerId__realName', 'racerId__gender',
                                               'teamId__name').filter(
            competitionId__uniname=self.kwargs['competition_uniname']).values('group', 'racerTag', 'racerId__realName',
                                                                              'racerId__gender', 'teamId__name')


class CompetitionDetailView(JsonViewMixin, BaseDetailView):
    def get_object(self, queryset=None):
        qs = Competition.objects.select_related('serialId__name').values()
        return get_object_or_404(qs, uniname=self.kwargs['competition_uniname'])
