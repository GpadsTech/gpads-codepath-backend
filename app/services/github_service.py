import re
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from app.exceptions.application_exceptions import ApplicationError
from app.integrations.github.github_client import GitHubFailure, GitHubPublisher
from app.integrations.github.github_mapper import GitHubMapper
from app.models.user import User
from app.repositories.interfaces.base import UnitOfWork
from app.services.common import conflict, leads, now, permit, require


class GitHubService:
    def __init__(
        self,
        uow: UnitOfWork,
        client: GitHubPublisher,
        allowed: set[str],
        owner: str = "",
    ):
        self.uow, self.client, self.allowed, self.owner = uow, client, allowed, owner
        self.mapper = GitHubMapper()

    def validate_target(self, actor, repository, path):
        repository = repository if "/" in repository else f"{self.owner}/{repository}"
        path = path.rstrip("/")
        valid_path = bool(path) and all(
            re.fullmatch(r"[A-Za-z0-9_-][A-Za-z0-9_.-]*", p) and p not in (".", "..")
            for p in path.split("/")
        )
        if (
            not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository)
            or not valid_path
        ):
            raise ApplicationError(
                "INVALID_GITHUB_TARGET", "Repositório ou caminho inválido."
            )
        prefixes = actor.publicationTargets.get(repository, [])
        permit(
            repository in self.allowed
            and any(
                prefix
                and (
                    path == prefix.rstrip("/")
                    or path.startswith(prefix.rstrip("/") + "/")
                )
                for prefix in prefixes
            )
        )
        return {"repository": repository, "path": path}

    def publish(self, actor, identifier):
        lease = uuid4().hex

        def claim(repos):
            report = require(repos.reports.get(identifier), "REPORT_NOT_FOUND")
            leader = User.from_document(
                require(repos.users.get(actor.id), "USER_NOT_FOUND")
            )
            permit(leads(leader, report["cellId"]) and actor.id != report["studentId"])
            conflict(report["status"] != "EVALUATED")
            github = report["github"]
            self.validate_target(leader, github["repository"], github["path"])
            if github["status"] in ("COMPLETED", "GITHUB_PUBLISHED"):
                return report
            conflict(
                github["status"] == "PROCESSING"
                and github.get("leaseUntil", "") > now(),
                "PUBLICATION_BUSY",
            )
            github.update(
                status="PROCESSING",
                leaseId=lease,
                leaseUntil=(datetime.now(UTC) + timedelta(minutes=5))
                .isoformat()
                .replace("+00:00", "Z"),
                attempts=github["attempts"] + 1,
                error=None,
            )
            repos.reports.patch(identifier, {"github": github})
            return report

        report = self.uow.run(claim)
        if report["github"]["status"] == "COMPLETED":
            return report
        if report["github"]["status"] == "GITHUB_PUBLISHED":
            return self._finish(
                identifier, report["github"].get("leaseId"), "COMPLETED"
            )
        # UID is used in the path but never trusted as path syntax.
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,128}", report["studentId"]):
            return self._finish(
                identifier, lease, "GITHUB_ERROR", error="INVALID_STUDENT_PATH"
            )
        try:
            files = self.client.publish(
                report["github"]["repository"], self.mapper.files(report)
            )
        except GitHubFailure as exc:
            return self._finish(identifier, lease, "GITHUB_ERROR", error=str(exc))
        self._finish(identifier, lease, "GITHUB_PUBLISHED", files=files)
        return self._finish(identifier, lease, "COMPLETED")

    def _finish(self, identifier, lease, status, **data):
        def operation(repos):
            report = require(repos.reports.get(identifier), "REPORT_NOT_FOUND")
            conflict(report["github"].get("leaseId") != lease, "PUBLICATION_LEASE_LOST")
            report["github"].update(data, status=status, updatedAt=now())
            repos.reports.patch(identifier, {"github": report["github"]})
            return report

        return self.uow.run(operation)
