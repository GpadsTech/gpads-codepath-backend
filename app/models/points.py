from dataclasses import dataclass
from datetime import datetime
from typing import Optional


MAX_POINTS = 100
MIN_POINTS = 0


@dataclass
class Points:
    student_id: str
    activity_id: str
    submission_id: str
    points: int
    evaluated_by: str
    created_at: Optional[datetime] = None
    source: str = "evaluation"

    def __post_init__(self):
        if not MIN_POINTS <= self.points <= MAX_POINTS:
            raise ValueError("A pontuação deve estar entre 0 e 100.")
