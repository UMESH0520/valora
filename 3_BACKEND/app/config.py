from __future__ import annotations

import os
from functools import lru_cache
from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "VALORA"
    frontend_url: str = os.getenv("FRONTEND_URL", "http://localhost:8080")

    # Pricing
    default_margin_percent: float = float(os.getenv("DEFAULT_MARGIN_PERCENT", 3.0))

    # CORS
    allow_origins: list[str] = [frontend_url, "http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:8080"]
    allow_credentials: bool = True
    allow_methods: list[str] = ["*"]
    allow_headers: list[str] = ["*"]

    # Algorand / Blockchain
    algod_address: str | None = os.getenv("ALGOD_ADDRESS")
    algod_api_token: str | None = os.getenv("ALGOD_API_TOKEN")
    oracle_mnemonic: str | None = os.getenv("ORACLE_MNEMONIC")
    app_id: int = int(os.getenv("APP_ID", "0"))


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
