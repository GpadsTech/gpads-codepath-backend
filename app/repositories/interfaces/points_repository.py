from typing import Protocol

from app.repositories.interfaces.base import DocumentRepository


class PointsRepository(DocumentRepository, Protocol):
    """Persistence contract for points documents."""
