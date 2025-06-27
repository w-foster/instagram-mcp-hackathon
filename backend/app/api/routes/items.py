# app/api/routes/items.py

from fastapi import APIRouter, HTTPException
from app.api.schemas.item_schemas import DeleteItemRequest
from app.services.supabase_client import get_all_items, insert_item, delete_item

from pipeline.end_to_end_pipeline import run_instagram_campaign, ProductPayload

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
    # INSERT INTO SUPABASE
    try:
        inserted = insert_item(item)

        # RUN CAMPAIGN FOR THIS PRODUCT
        payload = ProductPayload(
            title=item["product"],
            category=item["category"], 
            price=str(item["price"]),
            link=item["product_url"]
        )

        await run_instagram_campaign(payload)

        return inserted
    except Exception as e:
        print("Error inserting items to supabase")
        raise HTTPException(status_code=500, detail=str(e))



    


@router.delete("/")
async def delete_item_route(item: DeleteItemRequest):
    try:
        deleted = delete_item(item.id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Item not found")
        return {"message": "Item deleted successfully", "deleted": deleted}
    except Exception as e:
        print("Error deleting item from supabase")
        raise HTTPException(status_code=500, detail=str(e))
