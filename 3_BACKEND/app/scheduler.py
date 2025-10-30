from __future__ import annotations

import asyncio
import logging
import os
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Product
from app.services.price_service import compute

logger = logging.getLogger("valora.scheduler")


class PriceScheduler:
    def __init__(self, interval_seconds: int = 300, default_margin: float = 3.0) -> None:
        self.interval = interval_seconds
        self.default_margin = default_margin
        self._task: asyncio.Task | None = None
        self._stop = asyncio.Event()

    async def _run_once(self) -> None:
        db: Session = SessionLocal()
        try:
            products = db.query(Product).filter(Product.is_active == True).all()
            for p in products:
                try:
                    await compute(p.product_id, self.default_margin)
                except Exception:
                    logger.exception("compute failed for %s", p.product_id)
        finally:
            db.close()

    async def _loop(self) -> None:
        logger.info("PriceScheduler started with interval=%ss margin=%s%%", self.interval, self.default_margin)
        while not self._stop.is_set():
            try:
                await self._run_once()
            except Exception:
                logger.exception("scheduler iteration failed")
            try:
                await asyncio.wait_for(self._stop.wait(), timeout=self.interval)
            except asyncio.TimeoutError:
                continue

    def start(self) -> None:
        if self._task and not self._task.done():
            return
        interval = int(os.getenv("PRICE_POLL_INTERVAL_SECONDS", str(self.interval)))
        margin = float(os.getenv("DEFAULT_MARGIN_PERCENT", str(self.default_margin)))
        self.interval = interval
        self.default_margin = margin
        self._stop.clear()
        self._task = asyncio.create_task(self._loop())

    async def stop(self) -> None:
        self._stop.set()
        if self._task:
            try:
                await asyncio.wait_for(self._task, timeout=5)
            except Exception:
                pass


scheduler = PriceScheduler()
