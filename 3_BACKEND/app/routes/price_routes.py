from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.price_service import compute

router = APIRouter()

class PriceQuery(BaseModel):
    product_id: str
    margin_percent: float = 3.0

@router.post('/api/price')
async def price(q: PriceQuery):
    try:
        result = await compute(q.product_id, q.margin_percent)
        return result
    except KeyError:
        raise HTTPException(status_code=404, detail='product not found')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
