# schemas.py
from fastapi_users import schemas
from typing import Optional, Any
from pydantic import BaseModel

class UserRead(schemas.BaseUser[int]):
    pass

class UserCreate(schemas.BaseUserCreate):
    pass

class QuoteBase(BaseModel):
    title: Optional[str]
    data: Any

class QuoteCreate(QuoteBase):
    pass

class QuoteRead(QuoteBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True