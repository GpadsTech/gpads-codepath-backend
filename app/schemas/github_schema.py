from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.report import PublicationStatus


class GitHubPublishRequestSchema(BaseModel):
    repository: str
    path: str


class GitHubPublishResponseSchema(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    repository: str
    path: str
    status: PublicationStatus
    reference: Optional[str] = None
    error_message: Optional[str] = None
