import json
from collections import defaultdict
from fastapi import WebSocket


class Hub:
    """Channels: 'orders' (admin/pos/kitchen), 'rider:<id>', 'order:<id>' (customer tracking)."""

    def __init__(self) -> None:
        self.channels: dict[str, set[WebSocket]] = defaultdict(set)

    async def join(self, channel: str, ws: WebSocket) -> None:
        await ws.accept()
        self.channels[channel].add(ws)

    def leave(self, channel: str, ws: WebSocket) -> None:
        self.channels[channel].discard(ws)

    async def publish(self, channel: str, event: str, data: dict) -> None:
        msg = json.dumps({"event": event, "data": data}, default=str)
        dead = []
        for ws in list(self.channels[channel]):
            try:
                await ws.send_text(msg)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.leave(channel, ws)


hub = Hub()
