# app/services/mcp_client.py
# from your_mcp_client_library import Client  # placeholder

import httpx
from app.core.config import settings
from typing import Dict, Any

class MCPClient:
    def __init__(self, base_url: str = None):
        if base_url is None:
            base_url = settings.mcp_url
        self.base_url = base_url
        self.client = httpx.AsyncClient()

    async def get_user_posts(self, username: str, count: int = 12):
        response = await self.client.post(
            f"{self.base_url}/invoke",
            json={"tool": "get_user_posts", "args": {"username": username, "count": count}},
        )
        return response.json()

    async def send_message(self, username: str, message: str):
        response = await self.client.post(
            f"{self.base_url}/invoke",
            json={"tool": "send_message", "args": {"username": username, "message": message}},
        )
        return response.json()


def get_mcp_client():
    return MCPClient()