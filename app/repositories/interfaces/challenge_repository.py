from typing import Protocol

from app.repositories.interfaces.base import DocumentRepository


class ChallengeRepository(DocumentRepository, Protocol):
    """Persistence contract for challenge documents."""
