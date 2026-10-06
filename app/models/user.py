from dataclasses import dataclass
from enum import Enum
from typing import Optional


class UserRole(str, Enum):
    STUDENT = "student"
    CELL_LEADER = "cell_leader"
    ADMIN = "admin"


@dataclass
class User:
    uid: str
    name: str
    email: str
    role: UserRole
    cell_id: Optional[str] = None
    points: int = 0
    level: int = 1
