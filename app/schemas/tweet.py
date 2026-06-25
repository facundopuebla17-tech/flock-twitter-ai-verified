from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TweetCreate(BaseModel):
    content: str = Field(min_length=1, max_length=280)


class TweetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    author_id: UUID
    content: str
    created_at: datetime
