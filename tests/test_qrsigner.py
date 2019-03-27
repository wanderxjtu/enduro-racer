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
   File Name : test_qrsigner
   Author : jiaqi.hjq
"""

from certy import qrsigner
from enduro_racer import settings

qrs = """Jon Snow 雪20公开组1'20"333|MEYCIQDje/WkPy3sdPWEY5W2VdbNLKzGGN02pkKiFiouWATuPwIhAO5xM590pImmnKSKk9LM3/Z7thQZhyzf6p6j/Mnh4G2Y
"""
qrsigner.verify(settings.CERT_PUBKEY_PATH, qrs)
