# app/api/routes/items.py

from fastapi import APIRouter, HTTPException
from app.services.supabase_client import get_all_items, insert_item

router = APIRouter()

@router.get("/")
async def read_items():
    try:
        items = get_all_items()
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
async def create_item(item: dict):
    try:
        inserted = insert_item(item)
        return inserted
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
