import logging

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
        if isinstance(objs, QuerySet):
            objs = list(objs.values())
        return JsonResponse({objname: objs}, **response_kwargs)


class CompetitionListView(JsonListViewMixin, BaseListView):
    context_object_name = 'competitions'
    ordering = ["-startDate", "-endDate"]

    def get_queryset(self):
        if self.request.GET.get("showOpen", False) == "true":
            return Competition.objects.filter(signUpOpen=True)
        return Competition.objects.all()


class CompetitionDetailView(JsonViewMixin, BaseDetailView):
    def get_object(self, queryset=None):
        return get_object_or_404(Competition, uniname=self.kwargs['competition_uniname'])
