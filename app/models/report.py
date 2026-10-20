from dataclasses import dataclass
from enum import StrEnum


class ReportStatus(StrEnum):
    PENDING = "PENDING_EVALUATION"
    EVALUATED = "EVALUATED"
    REJECTED = "REJECTED"


class PublicationStatus(StrEnum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    PUBLISHED = "GITHUB_PUBLISHED"
    COMPLETED = "COMPLETED"
    ERROR = "GITHUB_ERROR"


@dataclass(frozen=True)
class Report:
    id: str
    studentId: str
    challengeId: str
    cellId: str
    description: str
    report: str
    code: str
    status: str
    submittedAt: str
    revision: int = 1
    evaluation: dict | None = None
    github: dict | None = None
