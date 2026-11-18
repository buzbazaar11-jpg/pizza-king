"""Haversine distance + delivery eligibility check."""
from math import radians, sin, cos, sqrt, atan2


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    R = 6371.0
    phi1, phi2 = radians(lat1), radians(lat2)
    d_phi = radians(lat2 - lat1)
    d_lam = radians(lng2 - lng1)
    a = sin(d_phi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(d_lam / 2) ** 2
    return 2 * R * atan2(sqrt(a), sqrt(1 - a))


def check_delivery(
    customer_lat: float,
    customer_lng: float,
    settings,          # DeliverySettings ORM row or dict-like
    areas: list,       # list[DeliveryArea]
) -> dict:
    center_lat = getattr(settings, "center_lat", 33.5651)
    center_lng = getattr(settings, "center_lng", 73.1486)
    free_radius = float(getattr(settings, "free_radius_km", 3.0))
    max_radius = float(getattr(settings, "max_radius_km", 7.0))
    base_charges = float(getattr(settings, "base_charges", 50.0))
    per_km = float(getattr(settings, "per_km_charges", 20.0))

    dist = haversine_km(center_lat, center_lng, customer_lat, customer_lng)

    if dist <= free_radius:
        return {
            "allowed": True,
            "charges": 0.0,
            "zone_name": "Free Delivery Zone",
            "reason": f"Within {free_radius} km free zone",
        }

    for area in areas:
        area_dist = haversine_km(
            float(area.lat), float(area.lng), customer_lat, customer_lng
        )
        if area_dist <= float(area.radius_km):
            return {
                "allowed": True,
                "charges": float(area.delivery_charges if hasattr(area, "delivery_charges") else area.fee),
                "zone_name": area.name,
                "reason": f"Within {area.name} delivery zone",
            }

    if dist <= max_radius:
        charges = base_charges + dist * per_km
        return {
            "allowed": True,
            "charges": round(charges, 2),
            "zone_name": "Standard Zone",
            "reason": f"{dist:.2f} km from center",
        }

    return {
        "allowed": False,
        "charges": 0.0,
        "zone_name": "",
        "reason": f"Location is {dist:.2f} km away, beyond the {max_radius} km limit",
    }
