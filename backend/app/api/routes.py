# app/api/routes.py

from fastapi import APIRouter, Depends, HTTPException
from app.services.mcp_client import MCPClient, get_mcp_client

router = APIRouter()

@router.get("/user_posts")
async def get_user_posts(username: str, count: int = 12, mcp: MCPClient = Depends(get_mcp_client)):
    result = await mcp.get_user_posts(username, count)
    if not result.get("success", False):
        raise HTTPException(status_code=404, detail=result.get("message", "Error fetching posts"))
    return result
