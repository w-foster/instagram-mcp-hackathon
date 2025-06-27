# app/services/supabase_client.py

from app.core.config import supabase

def get_all_items():
    response = supabase.table("discounts").select("*").execute()
    return response.data

def insert_item(data):
    response = supabase.table("discounts").insert(data).execute()
    return response.data

def delete_item(item_id: int):
    response = supabase.table("discounts").delete().eq("id", item_id).execute()
    return response.data
