import json
import os
from collections import defaultdict
# Create your views here.
from django.conf import settings
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

        basedir = settings.RESULT_BASE_PATH.format(name)

        conf = self._read_config(name)
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

    def _read_config(self, name):
        config = Competition.objects.values_list("resultConfig", flat=True).get(uniname=name)
        """
{"keys":["rank","no","name","team","start","end","certfilename","result","diff"],"cn":["排名","号码","姓名","车队","发车时间","撞线时间","","成绩","时间差"],"en":["Rank","No","Name","Team","StartAt","EndAt","","Result","Diff"],"th":["{rank[1]}<br>{rank[0]}","{no[1]}<br>{no[0]}","{name[1]}{name[0]}<br>{team[1]}{team[0]}","{start[1]}<br>{start[0]}","{end[1]}<br>{end[0]}","{result[1]}<br>{result[0]}","{diff[1]}<br>{diff[0]}"],"td":["{rank}","{no}","<p>{name}</p><p class="text-secondary">{team}</p>","{start}","{end}","<a href="{cert_link}">{result}</a>","{diff}"],"class":["","","","d-none d-lg-table-cell","d-none d-lg-table-cell","","d-none d-lg-table-cell"]}
        """
        print(config)
        return json.loads(config)
