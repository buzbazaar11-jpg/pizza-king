"""Analytics and reporting endpoints."""
from datetime import date, datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import role_required
from app.models.order import Order, OrderItem
from app.models.user import User
from app.schemas.report import DailySalesSummary, RevenueStats, TopItem, TopSellingItems

router = APIRouter(prefix="/reports", tags=["Reports"])

DB = Annotated[AsyncSession, Depends(get_db)]


def _period_start(period: str) -> datetime:
    now = datetime.now(timezone.utc)
    if period == "week":
        return now - timedelta(days=7)
    if period == "month":
        return now - timedelta(days=30)
    if period == "year":
        return now - timedelta(days=365)
    return now - timedelta(days=7)


@router.get("/daily", response_model=DailySalesSummary)
async def daily_report(
    db: DB,
    _: Annotated[User, Depends(role_required("admin", "staff"))],
    report_date: str = Query(default=None, alias="date"),
):
    if report_date:
        try:
            target = date.fromisoformat(report_date)
        except ValueError:
            target = date.today()
    else:
        target = date.today()

    day_start = datetime(target.year, target.month, target.day, 0, 0, 0, tzinfo=timezone.utc)
    day_end = day_start + timedelta(days=1)

    q = select(Order).where(
        Order.created_at >= day_start,
        Order.created_at < day_end,
        Order.status != "cancelled",
    )
    orders = (await db.execute(q)).scalars().all()

    total_orders = len(orders)
    total_revenue = sum(float(o.total) for o in orders)
    avg_order_value = total_revenue / total_orders if total_orders else 0.0

    by_source: dict = {}
    by_payment: dict = {}
    for o in orders:
        by_source[o.source] = by_source.get(o.source, 0) + float(o.total)
        by_payment[o.payment_method] = by_payment.get(o.payment_method, 0) + float(o.total)

    return DailySalesSummary(
        date=str(target),
        total_orders=total_orders,
        total_revenue=round(total_revenue, 2),
        avg_order_value=round(avg_order_value, 2),
        by_source=by_source,
        by_payment_method=by_payment,
    )


@router.get("/revenue", response_model=RevenueStats)
async def revenue_report(
    db: DB,
    _: Annotated[User, Depends(role_required("admin"))],
    period: str = Query(default="week"),
):
    since = _period_start(period)
    orders = (
        await db.execute(
            select(Order).where(Order.created_at >= since, Order.status != "cancelled")
        )
    ).scalars().all()

    # Group by date
    buckets: dict = {}
    for o in orders:
        day = o.created_at.strftime("%Y-%m-%d") if o.created_at else "unknown"
        if day not in buckets:
            buckets[day] = {"date": day, "revenue": 0.0, "orders": 0}
        buckets[day]["revenue"] += float(o.total)
        buckets[day]["orders"] += 1

    data = sorted(buckets.values(), key=lambda x: x["date"])
    return RevenueStats(period=period, data=data)


@router.get("/top-items", response_model=TopSellingItems)
async def top_items(
    db: DB,
    _: Annotated[User, Depends(role_required("admin"))],
    limit: int = Query(default=10),
    period: str = Query(default="week"),
):
    since = _period_start(period)
    rows = (
        await db.execute(
            select(
                OrderItem.food_id,
                OrderItem.name,
                func.sum(OrderItem.quantity).label("qty"),
                func.sum(OrderItem.line_total).label("rev"),
            )
            .join(Order, Order.id == OrderItem.order_id)
            .where(Order.created_at >= since, Order.status != "cancelled")
            .group_by(OrderItem.food_id, OrderItem.name)
            .order_by(func.sum(OrderItem.quantity).desc())
            .limit(limit)
        )
    ).all()

    items = [
        TopItem(food_id=row.food_id, title=row.name, quantity_sold=int(row.qty), revenue=float(row.rev))
        for row in rows
    ]
    return TopSellingItems(period=period, items=items)


@router.get("/riders")
async def rider_performance(
    db: DB,
    _: Annotated[User, Depends(role_required("admin"))],
):
    rows = (
        await db.execute(
            select(
                Order.rider_id,
                func.count(Order.id).label("deliveries"),
                func.sum(Order.total).label("earnings"),
            )
            .where(Order.rider_id.is_not(None), Order.status == "delivered")
            .group_by(Order.rider_id)
        )
    ).all()

    return [
        {
            "rider_id": row.rider_id,
            "deliveries": int(row.deliveries),
            "earnings": float(row.earnings or 0),
        }
        for row in rows
    ]
