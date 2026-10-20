import json
from dataclasses import asdict
from uuid import uuid4

from app.exceptions.application_exceptions import ApplicationError
from app.models.report import Report
from app.repositories.interfaces.base import UnitOfWork
from app.repositories.interfaces.repositories import Repositories
from app.services.common import can_read, conflict, now, permit, require


class ReportService:
    def __init__(self, repositories: Repositories, uow: UnitOfWork):
        self.repos, self.uow = repositories, uow

    def list(self, actor, pending=False):
        return sorted(
            [
                r
                for r in self.repos.reports.list()
                if can_read(actor, r)
                and (not pending or r["status"] == "PENDING_EVALUATION")
            ],
            key=lambda r: (r["submittedAt"], r["id"]),
            reverse=True,
        )

    def get(self, actor, identifier):
        report = require(self.repos.reports.get(identifier), "REPORT_NOT_FOUND")
        permit(can_read(actor, report))
        return report

    def create(self, actor, data):
        identifier, timestamp = uuid4().hex, now()

        def operation(repos):
            user = require(repos.users.get(actor.id), "USER_NOT_FOUND")
            permit(user.get("role") in ("student", "user") and bool(user.get("cellId")))
            challenge = require(
                repos.challenges.get(data["challengeId"]), "CHALLENGE_NOT_FOUND"
            )
            permit(not challenge.get("cellId") or challenge["cellId"] == user["cellId"])
            conflict(challenge["status"] != "active", "CHALLENGE_INACTIVE")
            report = asdict(
                Report(
                    id=identifier,
                    studentId=actor.id,
                    cellId=user["cellId"],
                    submittedAt=timestamp,
                    status="PENDING_EVALUATION",
                    **data,
                )
            )
            report["history"] = []
            self._check_size(report)
            repos.reports.create(identifier, report)
            return report

        return self.uow.run(operation)

    def resubmit(self, actor, identifier, data):
        def operation(repos):
            report = require(repos.reports.get(identifier), "REPORT_NOT_FOUND")
            permit(actor.id == report["studentId"])
            conflict(report["status"] != "REJECTED")
            history = report.get("history", []) + [
                {
                    k: report.get(k)
                    for k in (
                        "revision",
                        "description",
                        "report",
                        "code",
                        "submittedAt",
                        "evaluation",
                    )
                }
            ]
            report.update(
                data,
                status="PENDING_EVALUATION",
                submittedAt=now(),
                evaluation=None,
                revision=report["revision"] + 1,
                history=history,
            )
            self._check_size(report)
            repos.reports.patch(identifier, report)
            return report

        return self.uow.run(operation)

    @staticmethod
    def _check_size(report: dict) -> None:
        if len(json.dumps(report, ensure_ascii=False).encode("utf-8")) > 800_000:
            raise ApplicationError(
                "REPORT_TOO_LARGE", "Entrega e histórico excedem o limite de 800 KB."
            )
