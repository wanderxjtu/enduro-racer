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
from collections import defaultdict

from django.conf import settings


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


