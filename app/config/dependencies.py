import os
from functools import lru_cache

from app.config.firebase import FirebaseConfig
from app.integrations.github.github_client import GitHubClient
from app.middleware.auth_middleware import FirebaseTokenVerifier
from app.repositories.firebase.base import FirebaseUnitOfWork, make_repositories
from app.services.auth_service import AuthService
from app.services.challenge_service import ChallengeService
from app.services.dashboard_service import DashboardService
from app.services.evaluation_service import EvaluationService
from app.services.github_service import GitHubService
from app.services.points_service import PointsService
from app.services.ranking_service import RankingService
from app.services.report_service import ReportService
from app.services.user_service import UserService


class Container:
    def __init__(self, repositories, uow, verifier, publisher, allowed, owner=""):
        from app.services.ai_service import AIService
        self.ai = AIService(repositories, uow)
        from app.services.registration_service import RegistrationService
        self.registration = RegistrationService(repositories)
        self.auth = AuthService(verifier, repositories.users)
        self.points = PointsService(repositories.points)
        self.users = UserService(repositories.users, self.points)
        self.challenges = ChallengeService(repositories.challenges)
        self.reports = ReportService(repositories, uow)
        self.github = GitHubService(uow, publisher, allowed, owner)
        self.evaluations = EvaluationService(uow, self.points, self.github)
        self.ranking = RankingService(repositories)
        self.dashboard = DashboardService(
            self.points, self.ranking, self.reports, self.challenges
        )


@lru_cache(maxsize=1)
def get_container():
    db = FirebaseConfig().initialize()
    return Container(
        make_repositories(db),
        FirebaseUnitOfWork(db),
        FirebaseTokenVerifier(),
        GitHubClient(os.getenv("GITHUB_TOKEN", "")),
        set(filter(None, os.getenv("GITHUB_ALLOWED_REPOSITORIES", "").split(","))),
        os.getenv("GITHUB_OWNER", ""),
    )
