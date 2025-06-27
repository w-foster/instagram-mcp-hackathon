# app/services/supabase_client.py

from app.core.config import supabase

def get_all_items():
    response = supabase.table("discounts").select("*").execute()
    if response.error:
        raise Exception(response.error.message)
    return response.data

def insert_item(data):
    response = supabase.table("discounts").insert(data).execute()
    if response.error:
        raise Exception(response.error.message)
    return response.data
