from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class DeliveryStatus(str, Enum):
    PENDING_EVALUATION = "PENDING_EVALUATION"
    EVALUATED = "EVALUATED"
    REJECTED = "REJECTED"


class PublicationStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    GITHUB_PUBLISHED = "GITHUB_PUBLISHED"
    COMPLETED = "COMPLETED"
    GITHUB_ERROR = "GITHUB_ERROR"


@dataclass
class Evaluation:
    evaluated_by: str
    points: int
    final: bool = True
    feedback: Optional[str] = None
    evaluated_at: Optional[datetime] = None


@dataclass
class GitHubPublication:
    repository: str
    path: str
    status: PublicationStatus = PublicationStatus.PENDING
    reference: Optional[str] = None
    error_message: Optional[str] = None


@dataclass
class Report:
    id: str
    student_id: str
    challenge_id: str
    description: str
    report: Optional[str] = None
    code: Optional[str] = None
    status: DeliveryStatus = DeliveryStatus.PENDING_EVALUATION
    submitted_at: Optional[datetime] = None
    evaluation: Optional[Evaluation] = None
    github: Optional[GitHubPublication] = None
