import json
import os
from collections import defaultdict
# Create your views here.
from django.views.generic import TemplateView

from race.models.competition import Competition


class ResultView(TemplateView):
    template_name = "result.html"

    def get_context_data(self, **kwargs):
        compname = self.kwargs['competition_uniname']
        try:
            comp_full_name = Competition.objects.values_list("name", flat=True).get(uniname=compname)
        except Exception as e:
            comp_full_name = "比赛"

        headers, result = self._read_result(compname)

        return {"comp_full_name": comp_full_name,
                "result": result,
                "headers": headers}

    def _read_result(self, name):
        def _dict_formatter(d, formats):
            cert_link = "/certs/{}/{}".format(name, d["certfilename"]) if d["certfilename"] else ""
            return map(lambda x: x.format(**d, cert_link=cert_link), formats)

        basedir = "/home/admin/%s/" % name

        conf = self._read_config(basedir)
        keys = conf["keys"]
        cls = conf["class"]
        headers = zip(cls, _dict_formatter(dict(zip(keys,
                                                    zip(conf["en"], conf["cn"]))),
                                           conf["th"]))

        result = defaultdict(list)
        filepath = os.path.join(basedir, "result.csv")
        with open(filepath) as f:
            tdformat = conf["td"]
            for line in f:
                values = line.split(",")
                group = values[0].strip()
                data = dict(zip(keys, map(lambda s: s.strip("-"), map(str.strip, values[1:]))))
                result[group].append(zip(cls, _dict_formatter(data, tdformat)))

        return list(headers), dict(result)

    def _read_config(self, basedir):
        headerconfig = os.path.join(basedir, "header.json")
        with open(headerconfig) as f:
            conf = json.load(f)
            return conf
