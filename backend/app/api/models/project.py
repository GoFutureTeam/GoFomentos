from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid


class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    user_id: str
    edital_uuid: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    edital_uuid: Optional[str] = None


class ProjectInDB(ProjectBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Project(ProjectBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
