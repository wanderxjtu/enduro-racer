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
from collections import defaultdict

from django.conf import settings


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
