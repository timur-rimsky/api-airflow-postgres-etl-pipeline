from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserModel(BaseModel):
    external_id: int = Field(gt=0)
    name: str
    username: Optional[str] = None
    email: EmailStr
    phone: Optional[str] = None
    website: Optional[str] = None
    company_name: Optional[str] = None

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, value):
        if value.strip() == "":
            raise ValueError("name must not be empty")

        return value
