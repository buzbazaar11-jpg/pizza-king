"""FCM push notification dispatcher — graceful failure, never raises."""
import logging

import httpx

log = logging.getLogger("fcm")

FCM_URL = "https://fcm.googleapis.com/fcm/send"


async def send_push(token: str, title: str, body: str, data: dict | None = None) -> None:
    if not token:
        return
    payload = {
        "to": token,
        "notification": {"title": title, "body": body},
        "data": data or {},
    }
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(FCM_URL, json=payload)
            if not response.is_success:
                log.warning(
                    "FCM push failed: status=%s body=%s",
                    response.status_code,
                    response.text[:200],
                )
    except Exception as exc:
        log.error("FCM push error: %s", exc)
