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

    async def search_posts(self, tags: list[str], amount: int = 10):
        tools = await self.client.get_tools()
        search_tool = next(t for t in tools if t.name == "search_posts")
        resp = await search_tool.arun({
            "tags": tags,
            "amount": amount
        })
        return resp

    async def get_user_info(self, username: str):
        tools = await self.client.get_tools()
        user_info_tool = next(t for t in tools if t.name == "get_user_info")
        resp = await user_info_tool.arun({"username": username})
        return resp


async def main():
    insta = InstagramClient()
    send_resp = await insta.send_message("willzz._", "Hey Will, testing MCP directly!")
    print("send_message ->", send_resp)

    chats_resp = await insta.list_chats(5)
    print("list_chats ->", chats_resp)


if __name__ == "__main__":
    asyncio.run(main())
