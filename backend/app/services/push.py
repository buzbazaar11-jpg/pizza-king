"""FCM push. Configure FCM_SERVICE_ACCOUNT_FILE; otherwise pushes are skipped (logged)."""
import json
import logging
import time
import httpx
from jose import jwt
from app.core.config import settings

log = logging.getLogger("push")


async def _access_token(sa: dict) -> str:
    now = int(time.time())
    assertion = jwt.encode({"iss": sa["client_email"], "scope": "https://www.googleapis.com/auth/firebase.messaging",
                            "aud": "https://oauth2.googleapis.com/token", "iat": now, "exp": now + 3600},
                           sa["private_key"], algorithm="RS256")
    async with httpx.AsyncClient() as c:
        r = await c.post("https://oauth2.googleapis.com/token",
                         data={"grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer", "assertion": assertion})
        r.raise_for_status()
        return r.json()["access_token"]


async def send_push(tokens: list[str], title: str, body: str, data: dict | None = None) -> int:
    if not settings.FCM_SERVICE_ACCOUNT_FILE or not tokens:
        log.info("push skipped: %s", title)
        return 0
    with open(settings.FCM_SERVICE_ACCOUNT_FILE) as f:
        sa = json.load(f)
    token = await _access_token(sa)
    url = f"https://fcm.googleapis.com/v1/projects/{sa['project_id']}/messages:send"
    sent = 0
    async with httpx.AsyncClient() as c:
        for t in tokens:
            r = await c.post(url, headers={"Authorization": f"Bearer {token}"},
                             json={"message": {"token": t, "notification": {"title": title, "body": body},
                                               "data": {k: str(v) for k, v in (data or {}).items()}}})
            sent += r.is_success
    return sent
