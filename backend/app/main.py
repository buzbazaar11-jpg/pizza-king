"""FastAPI application entry point."""
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import async_engine
from app.core.security import decode_token
from app.services.websocket_manager import manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create all tables on startup (dev convenience — use Alembic for production)
    from app.core.database import Base
    import app.models  # noqa: F401 — registers all models with Base

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    await async_engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Production-ready FastAPI backend for Young Malang fast-food & POS platform",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API router
from app.api.v1.router import api_router  # noqa: E402

app.include_router(api_router, prefix="/api/v1")


# ── WebSocket ──────────────────────────────────────────────────────────────────

VALID_CHANNELS = {"pos", "kitchen", "rider"}


@app.websocket("/ws/{channel}")
async def websocket_endpoint(websocket: WebSocket, channel: str, token: str = None):
    if channel not in VALID_CHANNELS:
        await websocket.close(code=4004)
        return

    if token:
        payload = decode_token(token)
        if payload is None:
            await websocket.close(code=4001)
            return

    await manager.connect(websocket, channel)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(channel, {"event": "message", "data": data, "channel": channel})
    except WebSocketDisconnect:
        manager.disconnect(websocket, channel)


# ── Health check ───────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
async def health_check():
    return {"status": "ok", "app": settings.APP_NAME, "version": "1.0.0"}


# ── Exception handlers ─────────────────────────────────────────────────────────

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation error",
            "errors": exc.errors(),
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )
