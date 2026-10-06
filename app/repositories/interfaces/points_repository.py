from abc import ABC, abstractmethod
from typing import Optional, Sequence

from app.models.points import Points


class PointsRepository(ABC):
    @abstractmethod
    def create(self, points: Points) -> Points:
        raise NotImplementedError

    @abstractmethod
    def find_by_submission(self, submission_id: str) -> Optional[Points]:
        raise NotImplementedError

    @abstractmethod
    def find_by_student(self, student_id: str) -> Sequence[Points]:
        raise NotImplementedError

    @abstractmethod
    def find_history(self, student_id: str) -> Sequence[Points]:
        raise NotImplementedError

    @abstractmethod
    def total_by_student(self, student_id: str) -> int:
        raise NotImplementedError
