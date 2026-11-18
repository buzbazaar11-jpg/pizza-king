"""Database seeder — idempotent, safe to run multiple times."""
import asyncio
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.models.delivery import DeliverySettings
from app.models.loyalty import Coupon
from app.models.menu import Category, Food
from app.models.pos import PosTable
from app.models.user import User, UserRole


async def seed():
    async with AsyncSessionLocal() as db:
        await _seed_admin(db)
        await _seed_tables(db)
        await _seed_menu(db)
        await _seed_delivery(db)
        await _seed_coupons(db)
        await db.commit()
    print("Seed complete.")


async def _seed_admin(db: AsyncSession):
    existing = (await db.execute(select(User).where(User.email == "admin@youngmalang.com"))).scalar_one_or_none()
    if existing:
        print("Admin already exists, skipping.")
        return
    admin = User(
        email="admin@youngmalang.com",
        password_hash=hash_password("Admin@1234"),
        full_name="Admin User",
        is_active=True,
    )
    db.add(admin)
    await db.flush()
    db.add(UserRole(user_id=admin.id, role="admin"))
    print("Admin user created.")


async def _seed_tables(db: AsyncSession):
    existing_count = (await db.execute(select(PosTable))).scalars().all()
    if len(existing_count) >= 30:
        print("POS tables already seeded.")
        return
    for i in range(1, 31):
        exists = (await db.execute(select(PosTable).where(PosTable.number == i))).scalar_one_or_none()
        if not exists:
            db.add(PosTable(number=i, seats=4, status="available", qr_code=str(uuid.uuid4())))
    print("30 POS tables seeded.")


async def _seed_menu(db: AsyncSession):
    categories_data = [
        ("Burgers", "burgers"),
        ("Pizza", "pizza"),
        ("Deals", "deals"),
        ("Drinks", "drinks"),
        ("Sides", "sides"),
    ]

    foods_by_category = {
        "Burgers": [
            ("Classic Burger", 350),
            ("Cheese Burger", 420),
            ("Double Patty Burger", 550),
            ("Chicken Burger", 390),
            ("Spicy Burger", 400),
        ],
        "Pizza": [
            ("Margherita Pizza", 650),
            ("BBQ Chicken Pizza", 850),
            ("Pepperoni Pizza", 900),
            ("Veggie Pizza", 700),
            ("Spicy Pizza", 800),
        ],
        "Deals": [
            ("Family Deal 1", 1500),
            ("Couple Deal", 900),
            ("Student Deal", 450),
            ("Party Box", 2500),
            ("Budget Deal", 650),
        ],
        "Drinks": [
            ("Soft Drink 500ml", 100),
            ("Mineral Water", 60),
            ("Fresh Juice", 180),
            ("Milkshake", 250),
            ("Lassi", 150),
        ],
        "Sides": [
            ("French Fries", 200),
            ("Coleslaw", 120),
            ("Garlic Bread", 180),
            ("Onion Rings", 220),
            ("Nuggets (6pcs)", 280),
        ],
    }

    for cat_name, slug in categories_data:
        cat = (await db.execute(select(Category).where(Category.name == cat_name))).scalar_one_or_none()
        if not cat:
            cat = Category(name=cat_name, is_active=True)
            db.add(cat)
            await db.flush()
            print(f"Category '{cat_name}' created.")

        for food_name, price in foods_by_category.get(cat_name, []):
            exists = (await db.execute(select(Food).where(Food.name == food_name))).scalar_one_or_none()
            if not exists:
                db.add(Food(category_id=cat.id, name=food_name, price=price, is_available=True, is_featured=False))

    print("Menu seeded.")


async def _seed_delivery(db: AsyncSession):
    existing = (await db.execute(select(DeliverySettings).limit(1))).scalar_one_or_none()
    if existing:
        print("Delivery settings already seeded.")
        return
    db.add(
        DeliverySettings(
            center_name="Young Malang Main Branch",
            center_lat=33.5651,
            center_lng=73.1486,
            radius_km=7.0,
            base_fee=50.0,
            min_order=0.0,
            block_outside=True,
        )
    )
    print("Delivery settings seeded.")


async def _seed_coupons(db: AsyncSession):
    exists = (await db.execute(select(Coupon).where(Coupon.code == "WELCOME10"))).scalar_one_or_none()
    if not exists:
        db.add(
            Coupon(
                code="WELCOME10",
                discount_type="percent",
                value=10,
                min_order=500,
                max_uses=1000,
                is_active=True,
            )
        )
        print("Welcome coupon created.")


if __name__ == "__main__":
    asyncio.run(seed())
