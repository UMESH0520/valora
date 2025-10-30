from __future__ import annotations
import base64
from typing import Dict, Any, Optional
from algosdk.v2client import algod
from .settings import settings

_client: Optional[algod.AlgodClient] = None

def get_client() -> algod.AlgodClient:
    global _client
    if _client is None:
        headers = {settings.ALGOD_HEADER_KEY: settings.ALGOD_TOKEN} if settings.ALGOD_TOKEN else {}
        _client = algod.AlgodClient(settings.ALGOD_TOKEN, settings.ALGOD_ADDRESS, headers)
    return _client


def decode_global_state(global_state: list[dict]) -> Dict[str, Any]:
    decoded: Dict[str, Any] = {}
    for entry in global_state:
        key_b64 = entry.get("key")
        value = entry.get("value", {})
        if not key_b64:
            continue
        try:
            key = base64.b64decode(key_b64).decode()
        except Exception:
            key = key_b64
        vtype = value.get("type")
        if vtype == 1:
            b = value.get("bytes", "")
            try:
                decoded_val = base64.b64decode(b)
                try:
                    decoded_val = decoded_val.decode()
                except Exception:
                    pass
            except Exception:
                decoded_val = b
        else:
            decoded_val = value.get("uint")
        decoded[key] = decoded_val
    return decoded


def get_app_global_state(app_id: int) -> Dict[str, Any]:
    client = get_client()
    info = client.application_info(app_id)
    return decode_global_state(info["params"].get("global-state", []))


def get_price(product_id: Optional[str] = None) -> Optional[float]:
    """Fetch price from app global state. Looks for keys 'price:<product_id>' then 'price'."""
    if settings.APP_ID <= 0:
        return None
    state = get_app_global_state(settings.APP_ID)
    if product_id:
        key = f"price:{product_id}"
        if key in state:
            v = state[key]
            try:
                return float(v)
            except Exception:
                return None
    v = state.get("price")
    try:
        return float(v) if v is not None else None
    except Exception:
        return None
