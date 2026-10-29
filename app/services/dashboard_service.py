class LevelPolicy:
    """Preserve the provisioned level until an official progression rule exists."""

    def current(self, actor):
        return actor.level


class DashboardService:
    def __init__(self, points, ranking, reports, challenges, levels=None):
        self.points, self.ranking, self.reports, self.challenges = (
            points,
            ranking,
            reports,
            challenges,
        )
        self.levels = levels or LevelPolicy()

    def get(self, actor):
        reports = [r for r in self.reports.list(actor) if r["studentId"] == actor.id]
        activities = self.challenges.list(actor)
        evaluated = [r for r in reports if r["status"] == "EVALUATED"]
        active_ids = {c["id"] for c in activities}
        completed = {r["challengeId"] for r in evaluated}
        rank = self.ranking.me(actor)
        return {
            "points": self.points.total(actor.id),
            "level": self.levels.current(actor),
            "rankingPosition": rank["position"] if rank else None,
            "activities": activities,
            "completedChallenges": len(completed),
            "pendingReports": sum(r["status"] == "PENDING_EVALUATION" for r in reports),
            "evaluatedReports": len(evaluated),
            "rejectedReports": sum(r["status"] == "REJECTED" for r in reports),
            "progress": round(100 * len(completed & active_ids) / len(active_ids), 2)
            if active_ids
            else 0,
            "history": self.points.history(actor.id),
        }
