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

from .views import (CompetitionListView, CompetitionDetailView, IndexView, CompetitionGroupListView, TeamListView,
                    CompetitionSignupView, CompetitionSignupSuccessView)

urlpatterns = [
    path('', IndexView.as_view()),
    path('api/competitions/', CompetitionListView.as_view()),
    path('api/competition/<str:competition_uniname>', CompetitionDetailView.as_view()),
    path('api/competition/<str:competition_uniname>/signup/', CompetitionSignupView.as_view()),
    path('api/competition/<str:competition_uniname>/signup/success/', CompetitionSignupSuccessView.as_view()),
    path('api/competition/<str:competition_uniname>/result/', CompetitionDetailView.as_view()),
    path('api/competition/<str:competition_uniname>/group/', CompetitionGroupListView.as_view()),
    path('api/teams/', TeamListView.as_view()),
]
