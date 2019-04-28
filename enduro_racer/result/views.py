import json
import logging
import traceback

LOGGER = logging.getLogger(__name__)

# Create your views here.
from django.core.handlers import exception
from django.views.generic import TemplateView

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
            comp_obj = Competition.objects.values_list("name", "resultConfig",
                                                       named=True).get(uniname=compname)
            conf = json.loads(comp_obj.resultConfig)
            raw_result = read_result(compname, game, **conf)
            headers, result = self._render_format(compname, raw_result, **conf)

            return {"comp_full_name": comp_obj.name,
                    "result": result,
                    "headers": headers}
        except Exception:
            LOGGER.error(traceback.format_exc())
            raise exception.Http404()

    def _render_format(self, name, result, *, th, td, **conf):
        def _dict_formatter(d: dict, formats):
            cert_filename = d.get("certfilename") or CertGen(name, conf["certy"]).get_cert_filename(d["rank"],
                                                                                                    d["name"])
            cert_link = "/certs/{}/{}".format(name, cert_filename) if d["rank"] else ""
            # for now we can control the contents
            # d2 = {k: escape(v) for k, v in d.items()}
            return map(lambda x: x.format(**d, cert_link=cert_link), formats)

        cls = conf["class"]
        headers = zip(cls, th)
        for group, l in result.items():
            result[group] = (zip(cls, _dict_formatter(data, td)) for data in l)
        return list(headers), dict(result)
