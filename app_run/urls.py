from django.urls import path
from rest_framework.routers import DefaultRouter

from app_run.views import (
    company_details,
    RunViewSet,
    UserViewSet,
    StartView,
    FinishView,
    AthleteInfoView,
    ChallengeViewSet,
    PositionViewSet,
)


router = DefaultRouter()
router.register(r"runs", RunViewSet)
router.register(r"users", UserViewSet)
router.register(r"challenges", ChallengeViewSet)
router.register(r"positions", PositionViewSet)


urlpatterns = [
    path("company_details/", company_details, name="company-details"),
    path("runs/<int:run_id>/start/", StartView.as_view(), name="start-run"),
    path("runs/<int:run_id>/stop/", FinishView.as_view(), name="stop-run"),
    path("athlete_info/<int:user_id>/", AthleteInfoView.as_view(), name="athlete-info"),
]

urlpatterns += router.urls
