from app.models.user import User
from app.repositories.interfaces.base import UnitOfWork
from app.services.common import conflict, leads, now, permit, require


class EvaluationService:
    def __init__(self, uow: UnitOfWork, points, github):
        self.uow, self.points, self.github = uow, points, github

    def evaluate(self, actor, identifier, data):
        def operation(repos):
            report = require(repos.reports.get(identifier), "REPORT_NOT_FOUND")
            leader = User.from_document(
                require(repos.users.get(actor.id), "USER_NOT_FOUND")
            )
            student = require(repos.users.get(report["studentId"]), "USER_NOT_FOUND")
            existing = repos.points.get(identifier)
            permit(
                actor.id != report["studentId"]
                and leads(leader, report["cellId"])
                and student.get("cellId") == report["cellId"]
            )
            conflict(
                report["status"] != "PENDING_EVALUATION" or existing is not None,
                "ALREADY_EVALUATED",
            )
            timestamp = now()
            evaluation = {
                "evaluatedBy": actor.id,
                "createdAt": timestamp,
                "feedback": data["feedback"],
                "decision": data["decision"],
            }
            if data["decision"] == "reject":
                report.update(status="REJECTED", evaluation=evaluation)
            else:
                target = self.github.validate_target(
                    leader, data["repository"], data["path"]
                )
                point = self.points.record(report, data["points"], actor.id, timestamp)
                evaluation["points"] = data["points"]
                report.update(
                    status="EVALUATED",
                    evaluation=evaluation,
                    github={**target, "status": "PENDING", "attempts": 0},
                )
                repos.points.create(identifier, point)
            repos.reports.patch(identifier, report)
            return report

        report = self.uow.run(operation)
        if report["status"] == "EVALUATED":
            return self.github.publish(actor, identifier)
        return report
