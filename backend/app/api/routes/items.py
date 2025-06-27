# app/api/routes/items.py

from fastapi import APIRouter, HTTPException
from app.api.schemas.item_schemas import DeleteItemRequest
from app.services.supabase_client import get_all_items, insert_item, delete_item

router = APIRouter()

@router.get("/")
async def read_items():
    try:
        items = get_all_items()
        print(items)
        return items
    except Exception as e:
        print("Error returning items from supabase")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
async def create_item(item: dict):
    try:
        inserted = insert_item(item)
        return inserted
    except Exception as e:
        print("Error inserting items to supabase")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/delete")
async def delete_item_route(item: DeleteItemRequest):
    try:
        deleted = delete_item(item.id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Item not found")
        return {"message": "Item deleted successfully", "deleted": deleted}
    except Exception as e:
        print("Error deleting item from supabase")
        raise HTTPException(status_code=500, detail=str(e))
