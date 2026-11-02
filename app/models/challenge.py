from dataclasses import dataclass


@dataclass(frozen=True)
class Challenge:
    id: str
    title: str
    description: str
    createdAt: str
    status: str = "active"
    difficulty: str = "medium"
    cellId: str | None = None
    points: int = 0
