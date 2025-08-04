# auth.py
from fastapi import Depends
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import JWTStrategy, AuthenticationBackend, BearerTransport
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession
from models import User
from schemas import UserCreate, UserRead

SECRET = "SUPERSECRET"  # Replace with a real env var

bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

    return JWTStrategy(secret=SECRET, lifetime_seconds=60*60*24)

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

# AsyncSession dependency should be defined elsewhere, here's a stub:
async def get_async_session():
    ...

async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)

fastapi_users = FastAPIUsers[User, int](
    get_user_db,
    [auth_backend],
    User,
    UserCreate,
    UserRead,
    UserCreate,
    UserRead,
)
