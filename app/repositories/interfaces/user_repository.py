from typing import Protocol

from app.repositories.interfaces.base import DocumentRepository


class UserRepository(DocumentRepository, Protocol):
    """Persistence contract for user documents."""
