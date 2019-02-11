from django.urls import path

from .views import CompetitionListView, CompetitionDetailView, IndexView, CompetitionGroupListView

urlpatterns = [
    path('', IndexView.as_view()),
    path('api/competitions/', CompetitionListView.as_view()),
    path('api/competition/<str:competition_uniname>', CompetitionDetailView.as_view()),
    path('api/competition/<str:competition_uniname>/signup/', CompetitionDetailView.as_view()),
    path('api/competition/<str:competition_uniname>/result/', CompetitionDetailView.as_view()),
    path('api/competition/<str:competition_uniname>/group/', CompetitionGroupListView.as_view()),
]
