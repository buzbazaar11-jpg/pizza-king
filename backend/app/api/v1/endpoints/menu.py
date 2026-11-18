"""Menu — categories, food items, deals."""
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, role_required
from app.models.menu import Category, Deal, Food
from app.models.user import User
from app.schemas.menu import CategoryCreate, CategoryOut, DealCreate, DealOut, FoodCreate, FoodOut, FoodUpdate

router = APIRouter(prefix="/menu", tags=["Menu"])

DB = Annotated[AsyncSession, Depends(get_db)]


# ── Categories ────────────────────────────────────────────────────────────────

@router.get("/categories", response_model=list[CategoryOut])
async def list_categories(db: DB):
    rows = (await db.execute(select(Category).order_by(Category.sort_order))).scalars().all()
    return rows


@router.post("/categories", response_model=CategoryOut, status_code=201)
async def create_category(
    payload: CategoryCreate,
    db: DB,
    _: Annotated[User, Depends(role_required("admin", "staff"))],
):
    slug = payload.slug or payload.name.lower().replace(" ", "-")
    cat = Category(
        name=payload.name,
        image_url=payload.image_url,
        sort_order=payload.sort_order,
        is_active=payload.is_active,
    )
    db.add(cat)
    await db.commit()
    await db.refresh(cat)
    return cat


@router.put("/categories/{cat_id}", response_model=CategoryOut)
async def update_category(
    cat_id: str,
    payload: CategoryCreate,
    db: DB,
    _: Annotated[User, Depends(role_required("admin", "staff"))],
):
    cat = await db.get(Category, cat_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    for field, value in payload.model_dump(exclude_none=True).items():
        if field != "slug":
            setattr(cat, field, value)
    await db.commit()
    await db.refresh(cat)
    return cat


@router.delete("/categories/{cat_id}", status_code=204)
async def delete_category(
    cat_id: str,
    db: DB,
    _: Annotated[User, Depends(role_required("admin"))],
):
    cat = await db.get(Category, cat_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    await db.delete(cat)
    await db.commit()


# ── Food items ────────────────────────────────────────────────────────────────

@router.get("/items", response_model=list[FoodOut])
async def list_items(
    db: DB,
    category_id: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    featured: Optional[bool] = Query(None),
    skip: int = Query(0),
    limit: int = Query(100),
):
    q = select(Food).where(Food.is_available.is_(True))
    if category_id:
        q = q.where(Food.category_id == category_id)
    if search:
        q = q.where(Food.name.ilike(f"%{search}%"))
    if featured is not None:
        q = q.where(Food.is_featured.is_(featured))
    rows = (await db.execute(q.offset(skip).limit(limit))).scalars().all()
    return rows


@router.post("/items", response_model=FoodOut, status_code=201)
async def create_item(
    payload: FoodCreate,
    db: DB,
    _: Annotated[User, Depends(role_required("admin", "staff"))],
):
    food = Food(
        category_id=payload.category_id,
        name=payload.title,
        description=payload.description,
        price=payload.price,
        image_url=payload.image_url,
        is_available=payload.is_active,
        is_featured=payload.is_featured,
        sku=payload.sku,
        stock=payload.stock,
    )
    db.add(food)
    await db.commit()
    await db.refresh(food)
    return food


@router.put("/items/{item_id}", response_model=FoodOut)
async def update_item(
    item_id: str,
    payload: FoodUpdate,
    db: DB,
    _: Annotated[User, Depends(role_required("admin", "staff"))],
):
    food = await db.get(Food, item_id)
    if not food:
        raise HTTPException(status_code=404, detail="Food item not found")
    updates = payload.model_dump(exclude_none=True)
    if "title" in updates:
        food.name = updates.pop("title")
    if "is_active" in updates:
        food.is_available = updates.pop("is_active")
    for field, value in updates.items():
        if hasattr(food, field):
            setattr(food, field, value)
    await db.commit()
    await db.refresh(food)
    return food


@router.delete("/items/{item_id}", status_code=204)
async def delete_item(
    item_id: str,
    db: DB,
    _: Annotated[User, Depends(role_required("admin"))],
):
    food = await db.get(Food, item_id)
    if not food:
        raise HTTPException(status_code=404, detail="Food item not found")
    await db.delete(food)
    await db.commit()


# ── Deals ─────────────────────────────────────────────────────────────────────

@router.get("/deals", response_model=list[DealOut])
async def list_deals(db: DB):
    rows = (await db.execute(select(Deal).where(Deal.is_active.is_(True)))).scalars().all()
    return rows


@router.post("/deals", response_model=DealOut, status_code=201)
async def create_deal(
    payload: DealCreate,
    db: DB,
    _: Annotated[User, Depends(role_required("admin"))],
):
    deal = Deal(
        title=payload.title,
        description=payload.description,
        price=payload.deal_price,
        original_price=payload.original_price,
        image_url=payload.image_url,
        is_active=payload.is_active,
        items=[pid for pid in payload.food_item_ids],
    )
    db.add(deal)
    await db.commit()
    await db.refresh(deal)
    return deal


@router.put("/deals/{deal_id}", response_model=DealOut)
async def update_deal(
    deal_id: str,
    payload: DealCreate,
    db: DB,
    _: Annotated[User, Depends(role_required("admin"))],
):
    deal = await db.get(Deal, deal_id)
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    deal.title = payload.title
    deal.description = payload.description
    deal.price = payload.deal_price
    deal.original_price = payload.original_price
    deal.image_url = payload.image_url
    deal.is_active = payload.is_active
    deal.items = payload.food_item_ids
    await db.commit()
    await db.refresh(deal)
    return deal
