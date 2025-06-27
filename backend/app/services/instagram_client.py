# app/services/instagram_client.py

import asyncio
import os
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from app.core.config import settings
from langchain_mcp_adapters.client import MultiServerMCPClient
import json

load_dotenv()

class InstagramClient:
    def __init__(self):
        self.client = MultiServerMCPClient({
            "instagram_dm": {
                "url": settings.mcp_url,
                "transport": "streamable_http",
            }
        })
        self.tools = None

    async def initialize_tools(self):
        if self.tools is None:
            self.tools = await self.client.get_tools()

    def _get_tool(self, tool_name: str):
        if not self.tools:
            raise RuntimeError("Tools not loaded, call 'initialize_tools()' first.")
        tool = next((t for t in self.tools if t.name == tool_name), None)
        if not tool:
            raise ValueError(f"Tool '{tool_name}' not found among MCP tools.")
        return tool

    async def send_message(self, username: str, message: str) -> str:
        await self.initialize_tools()
        tool = self._get_tool("send_message")
        resp = await tool.arun({
            "username": username,
            "message": message
        })
        return resp

    async def list_chats(self, amount: int = 5) -> Dict[str, Any]:
        await self.initialize_tools()
        tool = self._get_tool("list_chats")
        resp = await tool.arun({"amount": amount})
        return resp

    async def list_pending_chats(self, amount: int = 20) -> Dict[str, Any]:
        await self.initialize_tools()
        tool = self._get_tool("list_pending_chats")
        resp = await tool.arun({"amount": amount})

        # Try to parse response if it's string
        if isinstance(resp, str):
            try:
                resp_dict = json.loads(resp)
            except Exception:
                # If can't parse JSON, wrap the response in an error dict
                resp_dict = {"success": False, "message": "Failed to parse response JSON", "raw_response": resp}
        elif isinstance(resp, dict):
            resp_dict = resp
        else:
            # Unexpected type, wrap in dict
            resp_dict = {"success": False, "message": "Unexpected response type", "raw_response": str(resp)}

        # Provide default keys to avoid AttributeErrors
        if "success" not in resp_dict:
            resp_dict["success"] = False
        if "threads" not in resp_dict:
            resp_dict["threads"] = []

        return resp_dict

    async def list_messages(self, thread_id: str, amount: int = 20) -> Dict[str, Any]:
        await self.initialize_tools()
        tool = self._get_tool("list_messages")
        resp = await tool.arun({
            "thread_id": thread_id,
            "amount": amount
        })
        return resp

    async def get_user_posts(self, username: str, count: int = 12) -> Dict[str, Any]:
        await self.initialize_tools()
        tool = self._get_tool("get_user_posts")
        resp = await tool.arun({
            "username": username,
            "count": count
        })
        return resp


async def main():
    insta = InstagramClient()

    # Send a message DM
    send_resp = await insta.send_message("willzz._", "Hey Will, testing MCP directly!")
    print("send_message ->", send_resp)

    # List recent chats
    chats_resp = await insta.list_chats(5)
    print("list_chats ->", chats_resp)

    # List pending chats
    pending_resp = await insta.list_pending_chats(10)
    print("list_pending_chats ->", pending_resp)

    # List messages in a specific thread (example thread id)
    if pending_resp.get("success") and pending_resp.get("threads"):
        thread_id = pending_resp["threads"][0].get("thread_id") or pending_resp["threads"][0].get("id")
        if thread_id:
            messages_resp = await insta.list_messages(thread_id, 15)
            print(f"list_messages for thread {thread_id} ->", messages_resp)

    # Get user posts
    posts_resp = await insta.get_user_posts("willzz._", 5)
    print("get_user_posts ->", posts_resp)


if __name__ == "__main__":
    asyncio.run(main())
