"""POS: tables, shifts, expenses."""
from datetime import datetime, timezone
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import role_required
from app.models.pos import PosExpense, PosShift, PosTable
from app.models.user import User
from app.schemas.pos import (
    ExpenseCreate,
    ExpenseOut,
    ShiftClose,
    ShiftCreate,
    ShiftOut,
    TableOut,
    TableStatusUpdate,
)

router = APIRouter(prefix="/pos", tags=["POS"])

DB = Annotated[AsyncSession, Depends(get_db)]
StaffDep = Annotated[User, Depends(role_required("admin", "staff"))]


@router.get("/tables", response_model=list[TableOut])
async def list_tables(db: DB, _: StaffDep):
    rows = (await db.execute(select(PosTable).order_by(PosTable.number))).scalars().all()
    return rows


@router.put("/tables/{table_id}/status", response_model=TableOut)
async def update_table_status(table_id: str, payload: TableStatusUpdate, db: DB, _: StaffDep):
    table = await db.get(PosTable, table_id)
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    valid_statuses = {"available", "occupied", "reserved", "cleaning"}
    if payload.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Status must be one of {valid_statuses}")
    table.status = payload.status
    await db.commit()
    await db.refresh(table)
    return table


@router.get("/shifts/active", response_model=Optional[ShiftOut])
async def get_active_shift(db: DB, current_user: StaffDep):
    row = (
        await db.execute(
            select(PosShift).where(
                PosShift.staff_id == current_user.id,
                PosShift.closed_at.is_(None),
            )
        )
    ).scalar_one_or_none()
    return row


@router.post("/shifts", response_model=ShiftOut, status_code=201)
async def open_shift(payload: ShiftCreate, db: DB, current_user: StaffDep):
    existing = (
        await db.execute(
            select(PosShift).where(
                PosShift.staff_id == current_user.id,
                PosShift.closed_at.is_(None),
            )
        )
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="You already have an active shift")
    shift = PosShift(
        staff_id=current_user.id,
        opening_cash=payload.opening_cash,
        notes=payload.notes,
    )
    db.add(shift)
    await db.commit()
    await db.refresh(shift)
    return shift


@router.put("/shifts/{shift_id}/close", response_model=ShiftOut)
async def close_shift(shift_id: str, payload: ShiftClose, db: DB, current_user: StaffDep):
    shift = await db.get(PosShift, shift_id)
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")
    if shift.staff_id != current_user.id:
        roles = [r.role for r in current_user.roles] if current_user.roles else []
        if "admin" not in roles:
            raise HTTPException(status_code=403, detail="Cannot close another staff's shift")
    shift.closing_cash = payload.closing_cash
    shift.closed_at = datetime.now(timezone.utc)
    if payload.notes:
        shift.notes = payload.notes
    await db.commit()
    await db.refresh(shift)
    return shift


@router.get("/shifts/{shift_id}/summary", response_model=ShiftOut)
async def shift_summary(shift_id: str, db: DB, _: StaffDep):
    shift = await db.get(PosShift, shift_id)
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")
    return shift


@router.get("/expenses", response_model=list[ExpenseOut])
async def list_expenses(
    db: DB,
    _: StaffDep,
    shift_id: Optional[str] = Query(None),
):
    q = select(PosExpense)
    # PosExpense doesn't have shift_id in the existing model; filter by staff if needed
    rows = (await db.execute(q.order_by(PosExpense.created_at.desc()))).scalars().all()
    return rows


@router.post("/expenses", response_model=ExpenseOut, status_code=201)
async def create_expense(payload: ExpenseCreate, db: DB, current_user: StaffDep):
    expense = PosExpense(
        staff_id=current_user.id,
        category=payload.category,
        description=payload.description,
        amount=payload.amount,
    )
    db.add(expense)
    await db.commit()
    await db.refresh(expense)
    return expense


@router.delete("/expenses/{expense_id}", status_code=204)
async def delete_expense(
    expense_id: str,
    db: DB,
    _: Annotated[User, Depends(role_required("admin"))],
):
    expense = await db.get(PosExpense, expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    await db.delete(expense)
    await db.commit()
