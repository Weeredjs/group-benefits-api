from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.quote import EmployerIn, QuoteOut
from app.db.session import get_session
from app.models import quote as models
from app.services import rate_engine

router = APIRouter(prefix="/quotes", tags=["quotes"])


@router.post("/", response_model=QuoteOut, status_code=status.HTTP_201_CREATED)
async def create_quote(payload: EmployerIn, db: AsyncSession = Depends(get_session)):
    """Ingest employer + employees, calculate premiums, return structured quote."""

    # 1️⃣ Persist Employer
    employer = models.Employer(
        name=payload.name,
        province=payload.province,
        industry_code=payload.industry_code,
    )
    db.add(employer)
    await db.flush()  # ensure PK available

    # 2️⃣ Persist Employees
    employees_db: list[models.Employee] = []
    for emp_in in payload.employees:
        emp_db = models.Employee(
            employer_id=employer.id,
            first_name=emp_in.first_name,
            last_name=emp_in.last_name,
            birth_date=emp_in.birth_date,
            coverage_tier=emp_in.coverage_tier,
            annual_salary=emp_in.annual_salary,
        )
        db.add(emp_db)
        employees_db.append(emp_db)

    # 3️⃣ Pricing
    total, line_items = await rate_engine.price(employer, payload.employees)

    # 4️⃣ Persist Quote + Lines
    quote_db = models.Quote(employer_id=employer.id, premium_total=total)
    db.add(quote_db)
    await db.flush()

    for li, emp_db in zip(line_items, employees_db):
        quote_line_db = models.QuoteLine(
            quote_id=quote_db.id,
            employee_id=emp_db.id,
            benefit_code=li.benefit_code,
            premium=li.premium,
        )
        db.add(quote_line_db)
        li.employee_id = emp_db.id  # patch response object

    await db.commit()

    return {
        "quote_id": quote_db.id,
        "premium_total": total,
        "line_items": line_items,
    }
