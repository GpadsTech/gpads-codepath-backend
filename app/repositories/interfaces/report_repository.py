from typing import Protocol

from app.repositories.interfaces.base import DocumentRepository


class ReportRepository(DocumentRepository, Protocol):
    """Persistence contract for report documents."""
