from pydantic import BaseModel
from dotenv import load_dotenv
import os
from typing import List

load_dotenv()

class Settings(BaseModel):
    ALGOD_ADDRESS: str = os.getenv("ALGOD_ADDRESS", "http://127.0.0.1:4001")
    ALGOD_TOKEN: str = os.getenv("ALGOD_TOKEN", "")
    ALGOD_HEADER_KEY: str = os.getenv("ALGOD_HEADER_KEY", "X-Algo-API-Token")
    APP_ID: int = int(os.getenv("APP_ID", "0"))
    POLL_SECONDS: int = int(os.getenv("POLL_SECONDS", "10"))
    CORS_ORIGINS: List[str] = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:8080,http://127.0.0.1:8080,http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")

settings = Settings()
