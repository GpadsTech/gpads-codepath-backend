from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.report import DeliveryStatus, PublicationStatus


class GitHubPublicationSchema(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    repository: str
    path: str
    status: PublicationStatus = PublicationStatus.PENDING
    reference: Optional[str] = None
    error_message: Optional[str] = None


class EvaluationSchema(BaseModel):
    evaluated_by: str
    points: int = Field(ge=0, le=100)
    final: bool = True
    feedback: Optional[str] = None
    evaluated_at: Optional[datetime] = None


class ReportCreateSchema(BaseModel):
    student_id: str = Field(min_length=1)
    challenge_id: str = Field(min_length=1)
    description: str = Field(min_length=1)
    report: Optional[str] = None
    code: Optional[str] = None

    @model_validator(mode="after")
    def validate_content(self):
        if not self.report and not self.code:
            raise ValueError("A entrega deve conter relatório, código ou ambos.")
        return self


class ReportResponseSchema(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    id: str
    student_id: str
    challenge_id: str
    description: str
    report: Optional[str] = None
    code: Optional[str] = None
    status: DeliveryStatus
    submitted_at: Optional[datetime] = None
    evaluation: Optional[EvaluationSchema] = None
    github: Optional[GitHubPublicationSchema] = None


class EvaluationRequestSchema(BaseModel):
    points: int = Field(ge=0, le=100)
    repository: str = Field(min_length=1)
    path: str = Field(min_length=1)
    feedback: Optional[str] = None


class EvaluationResponseSchema(EvaluationSchema):
    pass
