from __future__ import annotations

import asyncio
from typing import Dict, Set
from fastapi import WebSocket


class WebSocketManager:
    def __init__(self) -> None:
        self._connections: Dict[str, Set[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, product_id: str, ws: WebSocket) -> None:
        await ws.accept()
        async with self._lock:
            self._connections.setdefault(product_id, set()).add(ws)

    async def disconnect(self, product_id: str, ws: WebSocket) -> None:
        async with self._lock:
            if product_id in self._connections:
                self._connections[product_id].discard(ws)
                if not self._connections[product_id]:
                    del self._connections[product_id]

    async def broadcast(self, product_id: str, message: dict) -> None:
        async with self._lock:
            conns = list(self._connections.get(product_id, set()))
        if not conns:
            return
        to_remove: list[WebSocket] = []
        for ws in conns:
            try:
                await ws.send_json(message)
            except Exception:
                to_remove.append(ws)
        if to_remove:
            async with self._lock:
                for ws in to_remove:
                    self._connections.get(product_id, set()).discard(ws)


ws_manager = WebSocketManager()
