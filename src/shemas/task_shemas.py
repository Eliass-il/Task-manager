from typing import Annotated

from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    StringConstraints,
    field_validator,
)
from src.enum.enums import TaskStatus

TaskTitle = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=100,
    ),
]

class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    title: TaskTitle
    description: str | None = None
    status: TaskStatus
    due_at: AwareDatetime | None = None    
    created_at: AwareDatetime
    updated_at: AwareDatetime

class TaskCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: TaskTitle
    description: str | None = None
    status: TaskStatus = TaskStatus.TODO
    due_at: AwareDatetime | None = None

class TaskUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: TaskTitle | None = None
    description: str | None = None
    status: TaskStatus | None = None
    due_at: AwareDatetime | None = None

    @field_validator("title", "status", mode="before")
    @classmethod
    def reject_null(cls, value):
        if value is None:
            raise ValueError("Поле нельзя передавать как null")
        return value