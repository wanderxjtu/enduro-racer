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


def model_to_dict(model):
    if isinstance(model, Model):
        d = {}
        for f in model._meta.fields:
            d[f.name] = model_to_dict(getattr(model, f.name))
        return d
    return model


class IndexView(TemplateView):
    template_name = "index.html"


class JsonViewMixin:
    def render_to_response(self, context, **response_kwargs):
        obj = context['object']
        return JsonResponse({'object': model_to_dict(obj)}, **response_kwargs)


class JsonListViewMixin:
    def render_to_response(self, context, **response_kwargs):
        objname = self.get_context_object_name(context["object_list"])
        objs = context[objname]

        return JsonResponse({objname: [model_to_dict(obj) for obj in objs]}, **response_kwargs)


class CompetitionListView(JsonListViewMixin, BaseListView):
    context_object_name = 'competitions'
    ordering = ["-startDate", "-endDate"]

    def get_queryset(self):
        if self.request.GET.get("showOpen", False) == "true":
            return Competition.objects.filter(signUpOpen=True)
        return Competition.objects.all()


class CompetitionGroupListView(JsonListViewMixin, BaseListView):
    context_object_name = 'groups'

    def get_queryset(self):
        obj = get_object_or_404(Competition, uniname=self.kwargs['competition_uniname'])
        return RacerLog.objects.filter(competitionId=obj.id)


class CompetitionDetailView(JsonViewMixin, BaseDetailView):
    def get_object(self, queryset=None):
        return get_object_or_404(Competition, uniname=self.kwargs['competition_uniname'])
