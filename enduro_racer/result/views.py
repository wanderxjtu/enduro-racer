import json
import logging
import traceback

from functools import lru_cache

from race.models.racer import RacerLog

LOGGER = logging.getLogger(__name__)

# Create your views here.
from django.core.handlers import exception
from django.views.generic import TemplateView

from certy.certgen import CertGen
from race.models.competition import Competition
from result.read_result_csv import CsvResultReader, BBRawResultReader


class ResultView(TemplateView):
    template_name = "result.html"

    def get_result(self, compname, game, **conf):
        return CsvResultReader.read_result(compname, game, **conf)

    def get_context_data(self, **kwargs):
        compname = self.kwargs['competition_uniname']
        game = self.kwargs.get('game', None)

        try:
            comp_obj = Competition.objects.values_list("name", "resultConfig",
                                                       named=True).get(uniname=compname)
            conf = json.loads(comp_obj.resultConfig)
            raw_result = self.get_result(compname, game, **conf)
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


class BBResultView(ResultView):
    @lru_cache(maxsize=10)
    def get_racer_logs(self):
        ret = dict()
        for rec in RacerLog.objects.select_related('racerId__realName', 'teamId__name').filter(
                competitionId__uniname=self.kwargs['competition_uniname']).values('racerTag', 'racerId__realName',
                                                                                  'teamId__name'):
            ret[rec['racerTag']] = {'name': rec['racerId__realName'], 'team': rec['teamId__name']}
        return ret

    @property
    def result_reader(self):
        if not hasattr(self, "_result_reader"):
            self._result_reader = BBRawResultReader()
        return self._result_reader

    def get_result(self, compname, game, **conf):
        racer_infos = self.get_racer_logs()
        raw_result = self.result_reader.read_bb_raw_result(compname)
        for l in raw_result.values():
            for d in l:
                # query racerinfo then insert back to result dict
                # name/team
                d.update(racer_infos.get(d['no'], {'name': "UNKNOWN", 'team': "NOTEAM"}))
        return raw_result
