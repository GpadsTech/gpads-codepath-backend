from dataclasses import dataclass

from app.repositories.interfaces.challenge_repository import ChallengeRepository
from app.repositories.interfaces.points_repository import PointsRepository
from app.repositories.interfaces.report_repository import ReportRepository
from app.repositories.interfaces.user_repository import UserRepository


@dataclass
class Repositories:
    users: UserRepository
    challenges: ChallengeRepository
    reports: ReportRepository
    points: PointsRepository
