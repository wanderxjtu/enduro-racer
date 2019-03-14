from collections import defaultdict
from functools import partial

from django.shortcuts import render

# Create your views here.
from django.views.generic import TemplateView

RACE_NAME = {
    "sy0324": "2019中国绍兴上虞祝家庄国际单车速降赛"
}


class ResultView(TemplateView):
    template_name = "result.html"

    def get_context_data(self, **kwargs):
        compname = self.kwargs['competition_uniname']
        return {"compname": RACE_NAME.get(compname, "比赛"),
                "cert_prefix": "/cert/{}".format(compname),
                "result": self._read_result(compname)}

    def _read_result(self, name):
        filepath = "/home/admin/%s/result.csv"
        keys = ["rank", "no", "name", "team", "start", "end", "certfilename", "result", "diff", "points"]
        result = defaultdict(list)
        with open(filepath) as f:
            for line in f:
                values = line.split(",")
                group = values[0].strip()
                result[group].append(dict(zip(keys, map(lambda s: s.strip("-"),
                                                        map(str.strip, values[1:])))))

        for riderlist in result.values():
            riderlist.sort(key=lambda x: x["no"])
            riderlist.sort(key=lambda x: x["result"] or "99:99:99.999")

        return dict(result)
