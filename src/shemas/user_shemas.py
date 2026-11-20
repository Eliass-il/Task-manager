from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field, SecretStr

class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    email: EmailStr
    created_at: datetime

class UserCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr = Field(max_length=50)
    password: SecretStr = Field(min_length=10, max_length=128)

class UserSignIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr = Field(max_length=50)
    password: SecretStr = Field(min_length=1, max_length=128)  