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
import traceback
from datetime import datetime

LOGGER = logging.getLogger(__name__)
import json

from django.views.generic.edit import ProcessFormView
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404

from django.views.generic import TemplateView
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView

from .models.competition import Competition
from .models.racer import RacerLog, Team, RacerInfo


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
                                               'racerId__region', 'teamId__name').filter(
            competitionId__uniname=self.kwargs['competition_uniname']).values('group', 'racerTag', 'racerId__realName',
                                                                              'racerId__gender', 'racerId__region',
                                                                              'teamId__name')


class CompetitionDetailView(JsonViewMixin, BaseDetailView):
    # competition_fields = get_model_all_fields_names(Competition)

    def get_object(self, queryset=None):
        # print(self.competition_fields)
        qs = Competition.objects.select_related('serialId__name').values('serialId__name', 'name', 'location',
                                                                         'description', 'groupSetting',
                                                                         'startDate', 'endDate', 'signUpOpen',
                                                                         'uniname', 'signUpFee', 'signUpStartDate',
                                                                         'signUpEndDate', 'manager')
        return get_object_or_404(qs, uniname=self.kwargs['competition_uniname'])


class CompetitionSignupView(JsonViewMixin, ProcessFormView):
    success_url = "signup_success.html"

    def post(self, request, *args, **kwargs):
        request.META["CSRF_COOKIE_USED"] = True

        obj = json.loads(request.body.decode('utf-8'))
        try:
            succ, msg = self.validate(obj)
            if succ:
                self.save_object(obj)
            obj = {"success": succ, "message": msg}
        except Exception as e:
            LOGGER.error(traceback.format_exc())
            obj = {"success": False, "message": str(e)}
        return self.render_to_response({"object": obj})

    def save_object(self, obj):
        qs = RacerInfo.objects.all()
        try:
            idtype = 0 if obj["region"] == "CHN" else 1
            racer = qs.get(idType=idtype, idNumber=obj["idNumber"], realName=obj["realName"])
            # allow update some info
            racer.region = obj["region"]
            racer.phoneNumber = obj["phoneNumber"]
            racer.ecpName = obj["ecpName"]
            racer.ecpNumber = obj["ecpNumber"]
        except RacerInfo.DoesNotExist:
            # idtype is not posted here. check region instead.
            racer = RacerInfo(realName=obj["realName"], gender=obj["gender"], birthday=obj["birthday"],
                              region=obj["region"], idType=idtype, idNumber=obj["idNumber"],
                              phoneNumber=obj["phoneNumber"], ecpName=obj["ecpName"], ecpNumber=obj["ecpNumber"])
        racer.save()

        qs = Team.objects.all()
        if obj["teamId"] == "NEW":
            try:
                team = qs.get(name=obj["teamName"])
            except Team.DoesNotExist:
                team = Team(name=obj["teamName"], leaderName=obj["teamLeader"], leaderPhone=obj["teamLeaderPhone"])
        else:
            team = qs.get(id=obj["teamId"])
        team.save()

        comp = self.get_comp(uniname=self.kwargs['competition_uniname'])
        if RacerLog.objects.all().filter(racerId=racer, competitionId=comp).exists():
            return
        racerlog = RacerLog(racerId=racer, competitionId=comp, teamId=team, group=obj["group"])
        racerlog.save()

    def validate(self, obj):
        for k, v in obj.items():
            obj[k] = str(v).strip()

        if not self._is_phone_number(obj["phoneNumber"]):
            return False, "请填写正确的号码"

        obj["birthday"] = datetime.strptime(obj["birthday"].split("T")[0], "%Y-%m-%d")

        # check_racer_number
        comp = self.get_comp(uniname=self.kwargs['competition_uniname'])
        if obj["group"] not in comp.groupSetting.strip().split(','):
            return False, "请选择正确的分组".format(comp.manager)
        if not comp.signUpOpen:
            return False, "报名已关闭，请联系管理员！{}".format(comp.manager)
        if RacerLog.objects.filter(
                competitionId__uniname=self.kwargs['competition_uniname']).count() >= comp.maxRacerCount:
            return False, "报名人数已到上限，请联系管理员！{}".format(comp.manager)

        return True, ""

    def get_comp(self, **kwargs):
        return Competition.objects.all().get(**kwargs)

    def _is_phone_number(self, number: str):
        try:
            number = number.replace('-', '')
            if number.startswith('+'):
                number = number[1:]
            return number.isdigit() and len(number) >= 11
        except:
            return False

    def get_success_url(self, context):
        return self.request.path + "success/"


class TeamListView(JsonListViewMixin, BaseListView):
    context_object_name = 'teams'

    def get_queryset(self):
        return Team.objects.all().values('id', 'name', 'leaderName')


class CompetitionSignupSuccessView(TemplateView):
    template_name = "signup_success.html"
