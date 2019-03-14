from collections import defaultdict

from django.shortcuts import render

# Create your views here.
from django.views.generic import TemplateView


class ResultView(TemplateView):
    template_name = "result.html"

    def get_context_data(self, **kwargs):
        return {"compname": self.kwargs['competition_uniname'],
                "result": self._read_result(self.kwargs['competition_uniname'])}

    def _read_result(self, name):
        filepath = "/home/admin/%s/result.csv"
        keys = ["rank", "no", "name", "team", "start", "end", "result", "diff", "points"]
        result = defaultdict(list)
        with open(filepath) as f:
            for line in f:
                values = line.split(",")
                group = values[0].strip()
                result[group].append(dict(zip(keys, map(str.strip, values[1:]))))

        for riderlist in result.values():
            riderlist.sort(key=lambda x: x["no"])
            riderlist.sort(key=lambda x: x["result"] or "99:99:99.999")

        return dict(result)
