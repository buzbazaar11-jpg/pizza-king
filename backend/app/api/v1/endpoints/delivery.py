"""Delivery zone check and settings endpoints."""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import role_required
from app.models.delivery import DeliveryArea, DeliverySettings
from app.models.user import User
from app.schemas.delivery import (
    DeliveryAreaCreate,
    DeliveryAreaOut,
    DeliveryCheckIn,
    DeliveryCheckResult,
    DeliverySettingsOut,
    DeliverySettingsUpdate,
)
from app.services.distance_service import check_delivery

router = APIRouter(prefix="/delivery", tags=["Delivery"])

DB = Annotated[AsyncSession, Depends(get_db)]


@router.post("/check", response_model=DeliveryCheckResult)
async def check_delivery_zone(payload: DeliveryCheckIn, db: DB):
    settings_row = (await db.execute(select(DeliverySettings).limit(1))).scalar_one_or_none()
    areas = (
        await db.execute(select(DeliveryArea).where(DeliveryArea.is_active.is_(True)))
    ).scalars().all()
    result = check_delivery(payload.lat, payload.lng, settings_row, areas)
    return result


@router.get("/settings", response_model=DeliverySettingsOut)
async def get_settings(db: DB):
    row = (await db.execute(select(DeliverySettings).limit(1))).scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Delivery settings not configured")
    return row


@router.put("/settings", response_model=DeliverySettingsOut)
async def update_settings(
    payload: DeliverySettingsUpdate,
    db: DB,
    _: Annotated[User, Depends(role_required("admin"))],
):
    row = (await db.execute(select(DeliverySettings).limit(1))).scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Delivery settings not configured")
    for field, value in payload.model_dump(exclude_none=True).items():
        if hasattr(row, field):
            setattr(row, field, value)
    await db.commit()
    await db.refresh(row)
    return row


@router.get("/areas", response_model=list[DeliveryAreaOut])
async def list_areas(db: DB):
    rows = (await db.execute(select(DeliveryArea))).scalars().all()
    return rows


@router.post("/areas", response_model=DeliveryAreaOut, status_code=201)
async def create_area(
    payload: DeliveryAreaCreate,
    db: DB,
    _: Annotated[User, Depends(role_required("admin"))],
):
    area = DeliveryArea(
        name=payload.name,
        lat=payload.lat,
        lng=payload.lng,
        radius_km=payload.radius_km,
        fee=payload.delivery_charges,
        is_active=payload.is_active,
    )
    db.add(area)
    await db.commit()
    await db.refresh(area)
    return area


@router.put("/areas/{area_id}", response_model=DeliveryAreaOut)
async def update_area(
    area_id: str,
    payload: DeliveryAreaCreate,
    db: DB,
    _: Annotated[User, Depends(role_required("admin"))],
):
    area = await db.get(DeliveryArea, area_id)
    if not area:
        raise HTTPException(status_code=404, detail="Delivery area not found")
    area.name = payload.name
    area.lat = payload.lat
    area.lng = payload.lng
    area.radius_km = payload.radius_km
    area.fee = payload.delivery_charges
    area.is_active = payload.is_active
    await db.commit()
    await db.refresh(area)
    return area


@router.delete("/areas/{area_id}", status_code=204)
async def delete_area(
    area_id: str,
    db: DB,
    _: Annotated[User, Depends(role_required("admin"))],
):
    area = await db.get(DeliveryArea, area_id)
    if not area:
        raise HTTPException(status_code=404, detail="Delivery area not found")
    await db.delete(area)
    await db.commit()
