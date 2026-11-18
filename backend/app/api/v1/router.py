"""Aggregated API v1 router."""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, coupons, delivery, menu, orders, pos, reports, rider

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(menu.router)
api_router.include_router(orders.router)
api_router.include_router(delivery.router)
api_router.include_router(pos.router)
api_router.include_router(rider.router)
api_router.include_router(coupons.router)
api_router.include_router(reports.router)
