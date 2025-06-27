# app/api/schemas/item_schemas.py
from pydantic import BaseModel

class DeleteItemRequest(BaseModel):
    id: int
