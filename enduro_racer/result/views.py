import json
import os
from collections import defaultdict
# Create your views here.
from django.views.generic import TemplateView
from django.utils.html import escape

from certy.certgen import CertGen
from race.models.competition import Competition
from result.read_result_csv import read_result
from result.utils import read_config


class ResultView(TemplateView):
    template_name = "result.html"

    def get_context_data(self, **kwargs):
        compname = self.kwargs['competition_uniname']
        game = self.kwargs.get('game', None)
        try:
            comp_full_name = Competition.objects.values_list("name", flat=True).get(uniname=compname)
        except Exception as e:
            comp_full_name = "比赛"

        conf = read_config(compname)
        raw_result = read_result(compname, game, **conf)
        headers, result = self._render_format(compname, raw_result, **conf)

        return {"comp_full_name": comp_full_name,
                "result": result,
                "headers": headers}

    def _render_format(self, name, result, *, th, td, **conf):
        def _dict_formatter(d: dict, formats):
            d.setdefault("certfilename", CertGen(name).get_cert_filename(d["rank"], d["name"]))
            cert_link = "/certs/{}/{}".format(name, d["certfilename"]) if d["rank"] else ""
            # for now we can control the contents
            # d2 = {k: escape(v) for k, v in d.items()}
            return map(lambda x: x.format(**d, cert_link=cert_link), formats)

        cls = conf["class"]
        headers = zip(cls, th)
        for group, l in result.items():
            result[group] = (zip(cls, _dict_formatter(data, td)) for data in l)
        return list(headers), dict(result)
