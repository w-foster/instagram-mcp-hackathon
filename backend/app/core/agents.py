import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient

async def main():
    client = MultiServerMCPClient({
        "instagram_dm": {
            "url":       "http://localhost:8000/mcp",
            "transport": "streamable_http",
        }
    })
    tools = await client.get_tools()
    send_message_tool = next(t for t in tools if t.name == "send_message")
    list_chats_tool   = next(t for t in tools if t.name == "list_chats")

    # Pass a single dict into .arun()
    resp1 = await send_message_tool.arun({
        "username": "willzz._",
        "message":  "Hey Will, testing MCP directly!"
    })
    print("send_message ->", resp1)

    resp2 = await list_chats_tool.arun({
        "amount": 5
    })
    print("list_chats ->", resp2)

if __name__ == "__main__":
    asyncio.run(main())
