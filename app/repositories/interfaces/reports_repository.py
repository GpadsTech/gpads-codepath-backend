from abc import ABC, abstractmethod
from typing import Optional, Sequence

from app.models.report import DeliveryStatus, Report


class ReportRepository(ABC):
    @abstractmethod
    def create(self, report: Report) -> Report:
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, report_id: str) -> Optional[Report]:
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> Sequence[Report]:
        raise NotImplementedError

    @abstractmethod
    def list_by_status(self, status: DeliveryStatus) -> Sequence[Report]:
        raise NotImplementedError

    @abstractmethod
    def update(self, report: Report) -> Report:
        raise NotImplementedError
