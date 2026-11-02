from dataclasses import dataclass


@dataclass(frozen=True)
class Points:
    id: str
    studentId: str
    challengeId: str
    reportId: str
    activityId: str
    submissionId: str
    points: int
    evaluatedBy: str
    createdAt: str
    source: str = "evaluation"
