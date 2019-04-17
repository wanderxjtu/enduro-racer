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
   File Name : certgen_batch.py
   Author : jiaqi.hjq
"""
import sys
import django

from certy.competition_config import TEMPLATE_CONFIG

django.setup()

from certy.certgen import CertGen
from result.read_result_csv import read_result
from result.utils import read_config

RANK_FIXER = {
    "冠军": "1",
    "亚军": "2",
    "季军": "3",
    "荣誉领骑": "0",
}


def render_cert_batch(compname):
    # the cert should use on finals result, so no need to support game
    result = read_result(compname, **read_config(compname))
    g = CertGen(compname)
    for group, l in result.items():
        for data in l:
            if data["rank"]:
                rank = RANK_FIXER.get(data["rank"], data["rank"].lstrip("0"))
                filename = data.get("certfilename", g.get_cert_filename(rank, data["name"]))
                g.render_cert(data["name"], rank, group, data["result"], filename=filename)


if __name__ == "__main__":
    render_cert_batch(sys.argv[1])
