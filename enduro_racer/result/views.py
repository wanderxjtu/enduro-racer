from collections import defaultdict
# Create your views here.
from django.views.generic import TemplateView

from race.models.competition import Competition

RACE_NAME = {
    "sy2019s1": "2019绍兴·上虞丰惠祝家庄国际单车山地速降邀请赛",
    "nh2019s1": "2019宁海Enduro春季赛",
    "cat2019s1": "2019西湖小野猫Enduro赛",
}


class ResultView(TemplateView):
    template_name = "result.html"

    def get_context_data(self, **kwargs):
        compname = self.kwargs['competition_uniname']
        try:
            comp_full_name = Competition.objects.values_list("name", flat=True).get(uniname=compname)
        except Exception as e:
            comp_full_name = RACE_NAME.get(compname, "比赛")

        return {"comp_full_name": comp_full_name,
                "cert_prefix": "/certs/{}".format(compname),
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
