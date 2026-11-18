import math
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.models import DeliverySettings, DeliveryArea


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2 - lat1), math.radians(lng2 - lng1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


async def check_delivery(db: AsyncSession, lat: float, lng: float) -> dict:
    s = (await db.execute(select(DeliverySettings).limit(1))).scalar_one_or_none()
    clat = s.center_lat if s else settings.RESTAURANT_LAT
    clng = s.center_lng if s else settings.RESTAURANT_LNG
    radius = s.radius_km if s else settings.DELIVERY_RADIUS_KM
    base_fee = float(s.base_fee) if s else 0.0
    dist = round(haversine_km(clat, clng, lat, lng), 2)
    if dist <= radius:
        return {"allowed": True, "distance_km": dist, "fee": base_fee, "area": "Main zone"}
    areas = (await db.execute(select(DeliveryArea).where(DeliveryArea.is_active.is_(True)))).scalars().all()
    for a in areas:
        if haversine_km(a.lat, a.lng, lat, lng) <= a.radius_km:
            return {"allowed": True, "distance_km": dist, "fee": float(a.fee), "area": a.name}
    return {"allowed": False, "distance_km": dist, "fee": 0.0, "area": None,
            "reason": f"Outside {radius:g} km delivery radius"}
