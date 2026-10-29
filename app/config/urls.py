from django.http import JsonResponse
from django.urls import path


def health_check(request):
    """
    Endpoint simples utilizado para verificar se a API Django
    está funcionando corretamente.
    """
    return JsonResponse({"status": "ok", "message": "GPADS Backend está funcionando!"})


urlpatterns = [
    path("api/health/", health_check, name="health-check"),
]
from app.controllers.auth_controller import AuthController
from app.controllers.challenge_controller import (
    ChallengeController,
    ChallengeListController,
)
from app.controllers.dashboard_controller import DashboardController
from app.controllers.points_controller import PointsController, PointsHistoryController
from app.controllers.ranking_controller import RankingController, RankingMeController
from app.controllers.report_controller import (
    EvaluationController,
    PendingReportController,
    PublishController,
    ReportController,
    ReportListController,
    ResubmitController,
)
from app.controllers.user_controller import UserController

urlpatterns += [
    path("api/auth/me/", AuthController.as_view()),
    path("api/users/<str:userId>/", UserController.as_view()),
    path("api/users/<str:userId>/points/", PointsController.as_view()),
    path("api/users/<str:userId>/points/history/", PointsHistoryController.as_view()),
    path("api/challenges/", ChallengeListController.as_view()),
    path("api/challenges/<str:challengeId>/", ChallengeController.as_view()),
    path("api/reports/", ReportListController.as_view()),
    path("api/reports/pending/", PendingReportController.as_view()),
    path("api/reports/<str:reportId>/", ReportController.as_view()),
    path("api/reports/<str:reportId>/resubmit/", ResubmitController.as_view()),
    path("api/reports/<str:reportId>/evaluate/", EvaluationController.as_view()),
    path("api/reports/<str:reportId>/publish/", PublishController.as_view()),
    path("api/ranking/", RankingController.as_view()),
    path("api/ranking/me/", RankingMeController.as_view()),
    path("api/dashboard/", DashboardController.as_view()),
]

from app.controllers.ai_controller import AIController
urlpatterns += [path("api/ai/report/", AIController.as_view())]

from app.controllers.registration_controller import RegistrationController
urlpatterns += [path("api/students/", RegistrationController.as_view())]
