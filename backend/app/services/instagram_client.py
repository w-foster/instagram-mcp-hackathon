import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient

class InstagramClient:
    def __init__(self):
        self.client = MultiServerMCPClient({
            "instagram_dm": {
                "url":       "http://localhost:8000/mcp",
                "transport": "streamable_http",
            }
        })

    async def send_message(self, username: str, message: str):
        tools = await self.client.get_tools()
        send_message_tool = next(t for t in tools if t.name == "send_message")
        resp = await send_message_tool.arun({
            "username": username,
            "message": message
        })
        return resp

    async def list_chats(self, amount: int = 5):
        tools = await self.client.get_tools()
        list_chats_tool = next(t for t in tools if t.name == "list_chats")
        resp = await list_chats_tool.arun({"amount": amount})
        return resp

    async def get_user_posts(self, username: str, count: int = 12) -> Dict[str, Any]:
        tools = await self.client.get_tools()
        posts_tool = next(t for t in tools if t.name == "get_user_posts")
        return await posts_tool.arun({
            "username": username,
            "count": count
        })


async def main():
    insta = InstagramClient()
    send_resp = await insta.send_message("willzz._", "Hey Will, testing MCP directly!")
    print("send_message ->", send_resp)

    chats_resp = await insta.list_chats(5)
    print("list_chats ->", chats_resp)


if __name__ == "__main__":
    asyncio.run(main())
