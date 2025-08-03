"""
Group Benefits Quoting API – FastAPI entrypoint
Author: James Stirling
"""

import os
from datetime import datetime
from typing import Generator

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    DateTime,
    text,
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# ---------------------------------------------------------------------------
# Database configuration
# ---------------------------------------------------------------------------

DATABASE_URL: str | None = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Fail fast – Render will show this in the build logs
    raise RuntimeError(
        "DATABASE_URL environment variable not set. "
        "Add it via an Environment Group in the Render dashboard."
    )

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,       # drops stale connections
    pool_size=5,              # stays under Render free tier limit (20)
    max_overflow=0,           # do not open extra conns beyond pool_size
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ---------------------------------------------------------------------------
# ORM model
# ---------------------------------------------------------------------------


class Employer(Base):
    __tablename__ = "employers"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, nullable=False)
    contact_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    num_employees = Column(Integer, nullable=True)
    annual_payroll = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------


class EmployerCreate(BaseModel):
    company_name: str = Field(..., example="Acme Widgets Ltd.")
    contact_name: str = Field(..., example="Jane Doe")
    email: EmailStr = Field(..., example="jane.doe@example.com")
    phone: str = Field("", example="555-123-4567")
    num_employees: int | None = Field(None, example=25)
    annual_payroll: float | None = Field(None, example=1_300_000.00)


class EmployerOut(BaseModel):
    id: int
    company_name: str
    contact_name: str
    email: EmailStr
    phone: str | None = ""
    num_employees: int | None = None
    annual_payroll: float | None = None
    created_at: datetime

    class Config:
        orm_mode = True


# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------

app = FastAPI(title="Group Benefits Quoting API")


# -- Lifecycle events --------------------------------------------------------


@app.on_event("startup")
def on_startup() -> None:
    """Run once per process – create tables and warm a DB connection."""
    #Base.metadata.create_all(bind=engine)
    # quick ping to surface broken DATABASE_URL early
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))


# -- Dependency --------------------------------------------------------------


def get_db() -> Generator[Session, None, None]:
    """SQLAlchemy session generator (per-request)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -- Routes ------------------------------------------------------------------


@app.get("/", tags=["meta"])
def root() -> dict[str, str]:
    """Lightweight root ping (no DB)."""
    return {"status": "ok", "message": "Group Benefits Quoting API is live."}


@app.get("/healthz", tags=["meta"])
def healthz() -> dict[str, str]:
    """
    Deep health probe – used by Render's health-check path.
    Fails if the database is unreachable.
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:
        raise HTTPException(status_code=503, detail="Database unavailable")
    return {"status": "ok"}


@app.post("/employers", response_model=EmployerOut, tags=["employers"])
def create_employer(
    employer: EmployerCreate, db: Session = Depends(get_db)
) -> EmployerOut:
    db_employer = Employer(**employer.dict())
    db.add(db_employer)
    db.commit()
    db.refresh(db_employer)
    return db_employer


@app.get("/employers", response_model=list[EmployerOut], tags=["employers"])
def list_employers(
    limit: int = 20, db: Session = Depends(get_db)
) -> list[EmployerOut]:
    return (
        db.query(Employer)
        .order_by(Employer.created_at.desc())
        .limit(limit)
        .all()
    )
