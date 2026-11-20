"""Data gateway: the frontend talks ONLY to FastAPI.

FastAPI forwards database / auth / storage / functions / realtime traffic to
the Supabase project configured in backend/.env (SUPABASE_URL + keys).
The browser never knows the Supabase URL or keys. If FastAPI is stopped,
the frontend has no data.

Mounted at /gateway  ->  /gateway/rest/v1/..., /gateway/auth/v1/...,
/gateway/storage/v1/..., /gateway/functions/v1/..., /gateway/realtime/v1/websocket
"""
import asyncio

import httpx
from fastapi import APIRouter, HTTPException, Request, WebSocket
from fastapi.responses import Response

from app.core.config import settings

router = APIRouter(prefix="/gateway", tags=["Gateway"])

ALLOWED = ("rest/v1", "auth/v1", "storage/v1", "functions/v1")
# Placeholder key the frontend sends; replaced by the real anon key here.
PUBLIC_PLACEHOLDER = "fastapi-public"
HOP = {"host", "content-length", "connection", "accept-encoding", "transfer-encoding",
       "content-encoding", "keep-alive", "upgrade", "origin", "referer"}

_client: httpx.AsyncClient | None = None


def _upstream() -> tuple[str, str]:
    url = settings.SUPABASE_URL.rstrip("/")
    key = settings.SUPABASE_ANON_KEY
    if not url or not key:
        raise HTTPException(503, "SUPABASE_URL and SUPABASE_ANON_KEY must be set in backend/.env")
    return url, key


def _client_get() -> httpx.AsyncClient:
    global _client
    if _client is None:
        _client = httpx.AsyncClient(timeout=60.0)
    return _client


@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"])
async def forward(path: str, request: Request):
    if not path.startswith(ALLOWED):
        raise HTTPException(404, "Not found")
    base, anon = _upstream()
    headers = {k: v for k, v in request.headers.items() if k.lower() not in HOP}
    headers["apikey"] = anon
    auth = headers.get("authorization", "")
    if not auth or auth in (f"Bearer {PUBLIC_PLACEHOLDER}", f"Bearer {anon}"):
        headers.pop("authorization", None)
        if not anon.startswith("sb_"):  # legacy JWT anon keys must be sent as bearer
            headers["authorization"] = f"Bearer {anon}"
    body = await request.body()
    r = await _client_get().request(
        request.method, f"{base}/{path}", params=list(request.query_params.multi_items()),
        headers=headers, content=body,
    )
    out = {k: v for k, v in r.headers.items() if k.lower() not in HOP and not k.lower().startswith("access-control")}
    return Response(content=r.content, status_code=r.status_code, headers=out)


@router.websocket("/realtime/v1/websocket")
async def realtime(ws: WebSocket):
    import websockets

    base, anon = _upstream()
    await ws.accept()
    params = dict(ws.query_params)
    params["apikey"] = anon
    qs = "&".join(f"{k}={v}" for k, v in params.items())
    target = base.replace("https://", "wss://").replace("http://", "ws://") + f"/realtime/v1/websocket?{qs}"
    try:
        async with websockets.connect(target) as up:
            async def c2u():
                while True:
                    msg = await ws.receive_text()
                    await up.send(msg.replace(PUBLIC_PLACEHOLDER, anon))

            async def u2c():
                async for msg in up:
                    await ws.send_text(msg if isinstance(msg, str) else msg.decode())

            done, pending = await asyncio.wait(
                [asyncio.create_task(c2u()), asyncio.create_task(u2c())], return_when=asyncio.FIRST_COMPLETED)
            for t in pending:
                t.cancel()
    except Exception as e:
        print(f"[gateway] realtime closed: {e}")
    finally:
        try:
            await ws.close()
        except Exception:
            pass
