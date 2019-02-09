from django.urls import path

from .views import CompetitionListView, CompetitionDetailView, IndexView

urlpatterns = [
    path('', IndexView.as_view()),
    path('api/competitions/', CompetitionListView.as_view()),
    path('api/competition/<str:competition_uniname>', CompetitionDetailView.as_view()),
    path('api/competition/<str:competition_uniname>/signup/', CompetitionDetailView.as_view()),
    path('api/competition/<str:competition_uniname>/result/', CompetitionDetailView.as_view()),
    path('api/competition/<str:competition_uniname>/group/', CompetitionDetailView.as_view()),
]
