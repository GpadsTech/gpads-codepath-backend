from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.points import MAX_POINTS, MIN_POINTS


class PointsCreateSchema(BaseModel):
    student_id: str = Field(min_length=1)
    activity_id: str = Field(min_length=1)
    submission_id: str = Field(min_length=1)
    points: int = Field(ge=MIN_POINTS, le=MAX_POINTS)
    evaluated_by: str = Field(min_length=1)
    source: str = "evaluation"


class PointsResponseSchema(PointsCreateSchema):
    model_config = ConfigDict(from_attributes=True)

    created_at: Optional[datetime] = None
