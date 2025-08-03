"""SQLAlchemy 2.0 models for employers, employees, and quotes."""
import uuid
from decimal import Decimal
from sqlalchemy import Column, Date, ForeignKey, Numeric, String, UUID
from sqlalchemy.orm import Mapped, relationship
from app.db.base import Base


class Employer(Base):
    __tablename__ = "employers"

    id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = Column(String, nullable=False)
    province: Mapped[str] = Column(String(2), nullable=False)
    industry_code: Mapped[str] = Column(String(10), nullable=False)

    employees: Mapped[list["Employee"]] = relationship("Employee", back_populates="employer")
    quotes: Mapped[list["Quote"]] = relationship("Quote", back_populates="employer")


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employer_id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True), ForeignKey("employers.id", ondelete="CASCADE"))

    first_name: Mapped[str] = Column(String, nullable=False)
    last_name: Mapped[str] = Column(String, nullable=False)
    birth_date: Mapped[Date] = Column(Date, nullable=False)
    coverage_tier: Mapped[str] = Column(String(20), nullable=False)
    annual_salary: Mapped[Decimal] = Column(Numeric(10, 2), nullable=False)

    employer: Mapped["Employer"] = relationship("Employer", back_populates="employees")
    quote_lines: Mapped[list["QuoteLine"]] = relationship(
        "QuoteLine", back_populates="employee", cascade="all, delete-orphan"
    )


class Quote(Base):
    __tablename__ = "quotes"

    id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employer_id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True), ForeignKey("employers.id"))
    premium_total: Mapped[Decimal] = Column(Numeric(12, 2), nullable=False)

    employer: Mapped["Employer"] = relationship("Employer", back_populates="quotes")
    lines: Mapped[list["QuoteLine"]] = relationship(
        "QuoteLine", back_populates="quote", cascade="all, delete-orphan"
    )


class QuoteLine(Base):
    __tablename__ = "quote_lines"

    id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quote_id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True), ForeignKey("quotes.id", ondelete="CASCADE"))
    employee_id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"))

    benefit_code: Mapped[str] = Column(String(50), nullable=False)
    premium: Mapped[Decimal] = Column(Numeric(12, 2), nullable=False)

    quote: Mapped["Quote"] = relationship("Quote", back_populates="lines")
    employee: Mapped["Employee"] = relationship("Employee", back_populates="quote_lines")