#auth.py

from fastapi import Depends
from fastapi_users import FastAPIUsers, schemas
from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi_users.authentication import AuthenticationBackend, JWTStrategy
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.models import User
from app.api.deps import get_user_db

# --- User Schemas ---
class UserRead(schemas.BaseUser[int]):
    pass

class UserCreate(schemas.BaseUserCreate):
    pass

class UserUpdate(schemas.BaseUserUpdate):
    pass

class UserRead(schemas.BaseUser[int]):
    pass

# --- Auth Backend ---
SECRET = "YOUR_SUPER_SECRET"

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=None,  # No transport needed for JWT in v12+
    get_strategy=get_jwt_strategy,
)

# --- FastAPI Users Instance ---
fastapi_users = FastAPIUsers[User, int](
    get_user_db,
    [auth_backend],
    User,
    UserCreate,
    UserUpdate,
    UserRead,
)
