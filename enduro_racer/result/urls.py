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
   File Name : ${NAME}
   Author : jiaqi.hjq
"""
from django.urls import path
from django.views.decorators.cache import cache_page

from .views import ResultView

urlpatterns = [
    path('<str:competition_uniname>/', cache_page(15)(ResultView.as_view())),
    path('<str:competition_uniname>/<str:game>/', cache_page(15)(ResultView.as_view())),
]
