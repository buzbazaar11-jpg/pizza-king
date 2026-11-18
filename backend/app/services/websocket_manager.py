"""WebSocket connection manager — thin wrapper around realtime.Hub for named rooms."""
from app.services.realtime import hub


class ConnectionManager:
    """Facade that matches the interface described in the system prompt."""

    async def connect(self, ws, room: str) -> None:
        await hub.join(room, ws)

    def disconnect(self, ws, room: str) -> None:
        hub.leave(room, ws)

    async def broadcast(self, room: str, message: dict) -> None:
        await hub.publish(room, message.get("event", "message"), message)


manager = ConnectionManager()
