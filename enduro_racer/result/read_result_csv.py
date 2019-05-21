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
   File Name : read_result_csv
   Author : jiaqi.hjq
"""
import os
import logging

LOG = logging.getLogger(__file__)
from datetime import datetime, timedelta
from collections import defaultdict, OrderedDict

from django.conf import settings

from result.models import RacerResults, ResultsMeta


class CsvResultReader(object):
    @staticmethod
    def read_result(name, game=None, *, keys, **conf):
        basedir = settings.RESULT_BASE_PATH.format(name)

        result = defaultdict(list)
        filename = game or "result"
        filepath = os.path.join(basedir, filename + ".csv")
        with open(filepath) as f:
            for line in f:
                values = line.split(",")
                group = values[0].strip()
                data = dict(zip(keys, map(lambda s: s.strip("-"), map(str.strip, values[1:]))))
                result[group].append(data)
        return result


def load_hibp_dev_file(fpath):
    """
    Only read first effective data, ignore laters with same tag
    :param fpath:
    :return:
    """
    ret = dict()
    try:
        with open(fpath) as f:
            for line in f:
                if line.startswith('HIBP:'):
                    _, num, sec, ms = line.split('    ')  # four spaces
                    if num not in ret:
                        ret[num] = int(sec + ms)
    finally:
        return ret


class BBRawResultReader(object):
    """
    self.result = {"group": {no: result_ms, no_2: result_ms_2, ...}, group2_dict}
    """

    def __init__(self):
        self.result = OrderedDict()  # groups should be ordered

    def _get_raw_file_paires(self, name):
        basedir = settings.RESULT_BASE_PATH.format(name)
        ret = dict()
        for fn in os.listdir(basedir):
            if fn.startswith("end.txt"):
                _, postfix = fn.split(".txt", maxsplit=1)
                # it's ok to have ret['']
                ret[postfix] = (os.path.join(basedir, "start.txt" + postfix),
                                os.path.join(basedir, "end.txt" + postfix))
        return ret

    def _ms_to_tstr(self, msecs: int):
        secs, ms = divmod(msecs, 1000)
        return datetime.fromtimestamp(secs).strftime("%H:%M:%S") + ".{:03}".format(ms)

    def read_bb_raw_result(self, name, *args, **kwargs):
        """
        raw files should have info of (no group)
        HIBP:   no  ts_sec  ts_ms
        for balance bike
        all start at same time in one group
        result = first end ts - start ts
        skip numberplate that already in result[group]
        """
        for postfix, fs in self._get_raw_file_paires(name).items():
            if postfix != '' and postfix in self.result:
                # JUST READ ONCE for those already have result
                continue
            startts, endts = map(load_hibp_dev_file, fs)

            if '000' not in startts:
                continue
            start = startts['000']
            starttime = self._ms_to_tstr(start)

            try:
                meta = ResultsMeta(competition=name, displayname=postfix, resultId=postfix)
                meta.save()
            except Exception as e:
                # conflicted, should not happen.
                LOG.error("result meta save failed, skip reading. postfix={}, err={}".format(postfix, e))
                continue
            self.result[postfix] = list()

            rank_gen = iter(range(1, len(endts) + 1))
            first = True
            for num, end in sorted(endts.items(), key=lambda x: x[1]):
                result = endts[num] - start
                if first:
                    first = False
                    first_result = result
                try:
                    RacerResults(resultId=postfix, racerTag=num,
                                 launchTime=starttime, finishTime=self._ms_to_tstr(endts[num]),
                                 realResult=self._ms_to_tstr(result)).save()
                except Exception as e:
                    # conflicted, should not.
                    LOG.error("result save to db failed, id={}, racerTag={}, err={}".format(postfix, num, e))

                self.result[postfix].append({"rank": str(next(rank_gen)), "no": num, "start": starttime,
                                             "end": self._ms_to_tstr(endts[num]),
                                             "result": self._ms_to_tstr(result),
                                             "diff": self._ms_to_tstr(result - first_result)})
            # now move result to bak
            for f in fs:
                d = os.path.dirname(f)
                fn = os.path.basename(f)
                self._backup_file(f, os.path.join(d, postfix, fn))
        return self.result.copy()

    def _backup_file(self, src, dst):
        import pathlib
        try:
            ddir = os.path.dirname(dst)
            pathlib.Path(ddir).mkdir(parents=True, exist_ok=True)

            os.rename(src, dst)
        except Exception as e:
            LOG.warning("backup result file {} to {} failed: {}".format(src, dst, e))
