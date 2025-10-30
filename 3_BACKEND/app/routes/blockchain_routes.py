from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
from app.contracts.submitter import get_algod_client, submit_update, get_oracle_account

router = APIRouter(prefix="/api/blockchain", tags=["Blockchain"])

class SubmitRequest(BaseModel):
    product_id: str
    price_paise: int

@router.get("/health")
def health():
    configured = bool(os.getenv("ALGOD_ADDRESS") and os.getenv("ORACLE_MNEMONIC") and int(os.getenv("APP_ID") or 0) != 0)
    if not configured:
        return {"configured": False, "details": "Missing ALGOD_ADDRESS/ORACLE_MNEMONIC/APP_ID"}
    try:
        client = get_algod_client()
        status = client.status()
        return {"configured": True, "algod": {"last-round": status.get("last-round")}, "app_id": int(os.getenv("APP_ID"))}
    except Exception as e:
        return {"configured": True, "reachable": False, "error": str(e)}

@router.get("/address")
def address():
    """Return the derived public address from the configured mnemonic."""
    try:
        _, sender = get_oracle_account()
        return {"address": sender}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/submit")
def submit(req: SubmitRequest):
    try:
        result = submit_update(req.product_id, int(req.price_paise))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
