from datetime import datetime

from django.db.models import QuerySet
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

# Create your views here.
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.list import BaseListView

from .models.competition import Competition


class IndexView(TemplateView):
    template_name = "index.html"


class JsonViewMixin:
    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(**context, **response_kwargs)


class JsonListViewMixin:
    def render_to_response(self, context, **response_kwargs):
        objname = self.get_context_object_name(context["object_list"])
        objs = context[objname]
        if isinstance(objs, QuerySet):
            objs = list(objs.values())
        return JsonResponse({objname: objs}, **response_kwargs)


class CompetitionListView(JsonListViewMixin, BaseListView):
    context_object_name = 'competitions'
    queryset = Competition.objects.filter(signUpOpen=True)
    ordering = ["-startDate", "-endDate"]


class CompetitionDetailView(DetailView):
    # template_name = "competition.html"
    def get_object(self, queryset=None):
        return get_object_or_404(Competition, uniname=self.kwargs['competition_uniname'])
