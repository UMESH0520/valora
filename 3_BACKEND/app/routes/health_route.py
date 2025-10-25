from fastapi import APIRouter
router = APIRouter(tags=["System"])

@router.get('/api/health')
async def health():
    return {'status':'ok'}
