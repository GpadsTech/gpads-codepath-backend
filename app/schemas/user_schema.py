from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.user import UserRole


class UserResponseSchema(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    uid: str
    name: str
    email: str
    role: UserRole
    cell_id: Optional[str] = None
    points: int = 0
    level: int = 1
