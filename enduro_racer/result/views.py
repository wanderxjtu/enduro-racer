import json
import os
from collections import defaultdict
# Create your views here.
from django.conf import settings
from django.views.generic import TemplateView
from django.utils.html import escape

from race.models.competition import Competition


class ResultView(TemplateView):
    template_name = "result.html"

    def get_context_data(self, **kwargs):
        compname = self.kwargs['competition_uniname']
        game = self.kwargs.get('game', None)
        try:
            comp_full_name = Competition.objects.values_list("name", flat=True).get(uniname=compname)
        except Exception as e:
            comp_full_name = "比赛"

        headers, result = self._read_result(compname, game)

        return {"comp_full_name": comp_full_name,
                "result": result,
                "headers": headers}

    def _read_result(self, name, game=None):
        def _dict_formatter(d, formats):
            cert_link = "/certs/{}/{}".format(name, d["certfilename"]) if d["certfilename"] else ""
            return map(lambda x: x.format(**d, cert_link=cert_link), formats)

        basedir = settings.RESULT_BASE_PATH.format(name)

        conf = self._read_config(name)
        keys = conf["keys"]
        cls = conf["class"]
        headers = zip(cls, conf["th"])

        result = defaultdict(list)
        filename = game or "result"
        filepath = os.path.join(basedir, filename + ".csv")
        with open(filepath) as f:
            tdformat = conf["td"]
            for line in f:
                values = line.split(",")
                group = values[0].strip()
                data = dict(zip(keys, map(escape, map(lambda s: s.strip("-"), map(str.strip, values[1:])))))
                result[group].append(zip(cls, _dict_formatter(data, tdformat)))

        return list(headers), dict(result)

    def _read_config(self, name):
        config = Competition.objects.values_list("resultConfig", flat=True).get(uniname=name)
        return json.loads(config)
