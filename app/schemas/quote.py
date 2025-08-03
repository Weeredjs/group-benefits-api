"""Pydantic v3 request / response shapes."""
from datetime import date
from decimal import Decimal
from enum import Enum
from uuid import UUID
from pydantic import BaseModel, Field


class CoverageTier(str, Enum):
    single = "single"
    couple = "couple"
    family = "family"


class ProvinceCA(str, Enum):
    NS = "NS"
    NB = "NB"
    PE = "PE"
    NL = "NL"
    QC = "QC"
    ON = "ON"
    MB = "MB"
    SK = "SK"
    AB = "AB"
    BC = "BC"
    YT = "YT"
    NT = "NT"
    NU = "NU"


class EmployeeIn(BaseModel):
    first_name: str
    last_name: str
    birth_date: date
    coverage_tier: CoverageTier
    annual_salary: Decimal = Field(gt=0, decimal_places=2, max_digits=10)


class EmployerIn(BaseModel):
    name: str
    province: ProvinceCA
    industry_code: str
    employees: list[EmployeeIn]


class QuoteLineOut(BaseModel):
    employee_id: UUID
    benefit_code: str
    premium: Decimal


class QuoteOut(BaseModel):
    quote_id: UUID
    premium_total: Decimal
    line_items: list[QuoteLineOut]