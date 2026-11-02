from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from app.exceptions.application_exceptions import ApplicationError
from app.repositories.interfaces.repositories import Repositories


class RankingService:
    def __init__(self, repositories: Repositories):
        self.repos = repositories

    def list(self, period="all"):
        if period not in ("all", "week"):
            raise ApplicationError("INVALID_PERIOD", "Use all ou week.")
        current = datetime.now(ZoneInfo("America/Sao_Paulo"))
        start = (current - timedelta(days=current.weekday())).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        totals = {}
        for p in self.repos.points.list():
            date = datetime.fromisoformat(p["createdAt"])
            if period == "all" or start <= date <= current:
                totals[p["studentId"]] = totals.get(p["studentId"], 0) + p["points"]
        rows = [
            {
                "userId": u["id"],
                "name": u.get("name", ""),
                "points": totals.get(u["id"], 0),
                "level": u.get("level", 1),
            }
            for u in self.repos.users.list()
            if u.get("role") in ("student", "user")
        ]
        rows.sort(key=lambda row: (-row["points"], row["userId"]))
        previous, position = None, 0
        for index, row in enumerate(rows, 1):
            if row["points"] != previous:
                position = index
            row["position"] = position
            previous = row["points"]
        return rows

    def me(self, actor, period="all"):
        return next((r for r in self.list(period) if r["userId"] == actor.id), None)
