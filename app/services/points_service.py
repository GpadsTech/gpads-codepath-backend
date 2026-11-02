from dataclasses import asdict

from app.exceptions.application_exceptions import ApplicationError
from app.models.points import Points
from app.repositories.interfaces.points_repository import PointsRepository


class PointsService:
    def __init__(self, points: PointsRepository):
        self.points = points

    @staticmethod
    def record(report: dict, score: int, evaluator: str, timestamp: str) -> dict:
        if type(score) is not int or not 0 <= score <= 100:
            raise ApplicationError(
                "INVALID_POINTS", "A pontuação deve ser um inteiro de 0 a 100."
            )
        return asdict(
            Points(
                id=report["id"],
                studentId=report["studentId"],
                challengeId=report["challengeId"],
                reportId=report["id"],
                activityId=report["challengeId"],
                submissionId=report["id"],
                points=score,
                evaluatedBy=evaluator,
                createdAt=timestamp,
            )
        )

    def history(self, identifier):
        return sorted(
            [p for p in self.points.list() if p["studentId"] == identifier],
            key=lambda p: (p["createdAt"], p["id"]),
            reverse=True,
        )

    def total(self, identifier):
        return sum(p["points"] for p in self.history(identifier))
