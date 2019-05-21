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
   File Name : read_result_raw_bb
   Author : jiaqi.hjq
"""
import os
import traceback
from itertools import count
from collections import OrderedDict
from datetime import datetime, timedelta

from django.conf import settings

from race.models.competition import Competition
from result.models import ResultsMeta, RacerResults
from result.read_result_csv import load_hibp_dev_file, LOG


class BBRawResultReader(object):
    """
    self.result = {"group": {no: result_ms, no_2: result_ms_2, ...}, group2_dict}
    """

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

    def _misecs_to_datetime(self, msecs: int):
        secs = float(msecs) / 1000
        return datetime.fromtimestamp(secs)

    def read_result(self, name, *args, **kwargs):
        """
        load result form db first
        then from txt file
        """
        db_r, loaded = self.read_result_from_db(name)
        txt_r = self.read_result_from_file(name, loaded_postfixes=loaded)
        txt_r.update(db_r)
        return txt_r

    def read_result_from_db(self, name):
        result = OrderedDict()
        loaded_postfixes = list()
        for row in ResultsMeta.objects.filter(competition__uniname=name, valid=True).values('resultId', 'displayname'):
            postfix = row['resultId']
            loaded_postfixes.append(postfix)
            displayname = row['displayname']

            result[displayname] = list()
            rankcnt = count(1)
            db_result = RacerResults.objects.filter(resultId=postfix).values('racerTag', 'launchTime',
                                                                             'finishTime', 'realResult',
                                                                             'punishment')
            for row in db_result:
                row['result'] = row['realResult'] + timedelta(seconds=row['punishment'])

            for row in sorted(db_result, key=lambda x: x['result']):
                rank = next(rankcnt)
                if rank == 1:
                    first = row['result']
                result[displayname].append({"rank": str(rank), "no": row['racerTag'],
                                            "start": row['launchTime'].strftime("%H:%M:%S.%f")[:-3],
                                            "end": row['finishTime'].strftime("%H:%M:%S.%f")[:-3],
                                            "result": row['result'].strftime("%H:%M:%S.%f")[:-3],
                                            "punishment": str(row['punishment']),
                                            "diff": str(row['result'] - first)[:-3],
                                            })
        return result, loaded_postfixes

    def read_result_from_file(self, name, *, loaded_postfixes=None):
        """
        raw files should have info of (no group)
        HIBP:   no  ts_sec  ts_ms
        for balance bike
        all start at same time in one group
        result = first end ts - start ts
        skip numberplate that already in result[group]
        """
        loaded_postfixes = loaded_postfixes or list()
        result = OrderedDict()
        for postfix, fs in self._get_raw_file_paires(name).items():
            if postfix != '' and postfix in loaded_postfixes:
                # JUST READ ONCE for those already have result
                continue
            startts, endts = map(load_hibp_dev_file, fs)

            if '000' not in startts:
                continue
            start = startts['000']
            starttime = self._misecs_to_datetime(start)

            try:
                if postfix:
                    meta = ResultsMeta(competition=Competition.objects.get(uniname=name),
                                       displayname=postfix, resultId=postfix)
                    meta.save()
            except Exception as e:
                print(traceback.format_exc())
                # conflicted, should not happen.
                LOG.error("result meta save failed, skip reading. comp={}, postfix={}, err={}".format(name, postfix, e))
                continue
            displayname = postfix or "Ongoing"
            result[displayname] = list()
            loaded_postfixes.append(postfix)

            rankcnt = count(1)
            for num, end in sorted(endts.items(), key=lambda x: x[1]):
                resulttime = endts[num] - start
                rank = next(rankcnt)
                if rank == 1:
                    first = resulttime
                try:
                    if postfix and meta:
                        RacerResults(resultId=meta, racerTag=num,
                                     launchTime=starttime, finishTime=self._misecs_to_datetime(endts[num]),
                                     realResult=self._misecs_to_datetime(resulttime), punishment=0).save()
                except Exception as e:
                    # conflicted, should not.
                    LOG.error("result save to db failed, id={}, racerTag={}, err={}".format(postfix, num, e))

                result[displayname].append(
                    {"rank": str(rank), "no": num, "start": starttime.strftime("%H:%M:%S.%f")[:-3],
                     "end": self._misecs_to_datetime(endts[num]).strftime("%H:%M:%S.%f")[:-3],
                     "result": self._misecs_to_datetime(resulttime).strftime("%H:%M:%S.%f")[:-3],
                     "punishment": "0",
                     "diff": self._misecs_to_datetime(resulttime - first).strftime("%H:%M:%S.%f")[:-3]})
            # now move result to bak
            if postfix:
                for f in fs:
                    d = os.path.dirname(f)
                    fn = os.path.basename(f)
                    self._backup_file(f, os.path.join(d, datetime.today().strftime("%Y-%m-%d"), fn))
        return result

    def _backup_file(self, src, dst):
        import pathlib
        try:
            ddir = os.path.dirname(dst)
            pathlib.Path(ddir).mkdir(parents=True, exist_ok=True)

            os.rename(src, dst)
        except Exception as e:
            LOG.warning("backup result file {} to {} failed: {}".format(src, dst, e))
