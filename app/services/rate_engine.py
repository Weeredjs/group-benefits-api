"""Thin placeholder – will delegate to external‑rates service in phase 2."""
from decimal import Decimal
from typing import List
from app.schemas.quote import EmployeeIn, QuoteLineOut


async def price(_, employees: List[EmployeeIn]):  # employer not yet used
    """Flat CA$100 per employee – replace with actuarial calc later."""
    total = Decimal("0")
    lines: list[QuoteLineOut] = []
    for emp in employees:
        premium = Decimal("100.00")
        total += premium
        lines.append(
            QuoteLineOut(
                employee_id=None,  # filled in API layer after persistence
                benefit_code="BASIC_HEALTH",
                premium=premium,
            )
        )
    return total, lines