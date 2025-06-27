import asyncio
from typing import Dict, Any, List
from langgraph_supervisor import create_supervisor
from langgraph.prebuilt import create_react_agent
from langgraph.graph import MessagesState
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI

from pipeline.agentic import create_dm_supervisor


class CampaignState(MessagesState):
    product: Dict[str, Any] = {}
    hashtags: List[str] = []
    target_usernames: List[str] = []
    current_username: str = ""
    profile_analysis: Dict[str, Any] = {}
    draft_message: str = ""
    verification_result: Dict[str, Any] = {}
    sent_messages: List[Dict] = []


supervisor = create_dm_supervisor()