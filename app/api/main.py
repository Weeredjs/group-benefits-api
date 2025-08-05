from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from .auth import fastapi_users, auth_backend
from app.db.session import get_session as get_async_session
from .schemas import UserRead, QuoteCreate, QuoteRead
from .models import Base, Quote
from sqlalchemy import select
from app.api.user_manager import get_user_manager
import os

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable not set!")
from app.api.user_manager import get_user_manager
from app.api.auth import auth_backend
from fastapi_users import FastAPIUsers
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
fastapi_users = FastAPIUsers(
    get_user_manager,  # <--- NEW: user manager dependency
    [auth_backend],    # <--- list of auth backends
)
engine = create_async_engine(DATABASE_URL, echo=True)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

app = FastAPI()
# CORS for local and production frontend:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://yourdomain.com", "https://quote.yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables on startup:
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Include FastAPI Users routes
app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(), prefix="/auth", tags=["auth"]
)
app.include_router(
    fastapi_users.get_users_router(), prefix="/users", tags=["users"]
)

current_active_user = fastapi_users.current_user(active=True)

# CRUD endpoints for quotes (save/load per user)
@app.post("/quotes/", response_model=QuoteRead)
async def create_quote(
    quote: QuoteCreate,
    user: UserRead = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    new_quote = Quote(user_id=user.id, title=quote.title, data=quote.data)
    session.add(new_quote)
    await session.commit()
    await session.refresh(new_quote)
    return new_quote

@app.get("/quotes/", response_model=list[QuoteRead])
async def get_quotes(
    user: UserRead = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    result = await session.execute(
        select(Quote).where(Quote.user_id == user.id)
    )
    return result.scalars().all()
