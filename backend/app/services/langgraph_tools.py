# app/services/langgraph_tools.py

from langgraph import LangGraph, tool

from app.services.mcp_server import get_user_posts
from app.services.llm_client import LLMClient

llm = LLMClient()

@tool()
async def get_posts_tool(username: str, count: int = 12):
    posts = await get_user_posts(username, count)
    # Maybe enrich or filter posts before returning
    return posts

# Setup LangGraph graph here if needed, orchestrating tools and LLM
