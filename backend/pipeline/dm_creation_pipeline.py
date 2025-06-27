import asyncio
import os
from typing import Dict, Any, List
from langgraph_supervisor import create_supervisor
from langgraph.prebuilt import create_react_agent
from langgraph.graph import MessagesState
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langchain_core.messages import convert_to_messages
from pydantic import BaseModel

from pipeline.dm_creation_prompts import profile_analyzer_prompt, verifier_prompt, message_writer_prompt, supervisor_prompt


MODEL = "o4-mini"
PROVIDER = "openai"

# class CampaignState(MessagesState):
#     product: Dict[str, Any] = {}
#     current_username: str = ""
#     profile_analysis: Dict[str, Any] = {}
#     draft_message: str = ""
#     verification_result: Dict[str, Any] = {}
    
#     remaining_steps: int = 10
#     is_last_step: bool = False


class DMResult(BaseModel):
    final_dm: str
    target_user: str
    verification_status: str



async def setup_instagram_tools(filter_tools=None):
    """Setup MCP client to get Instagram tools via HTTP"""
    
    client = MultiServerMCPClient({
        "instagram_dm": {
            "url": "http://localhost:8000/mcp",
            "transport": "streamable_http",
        }
    })
    
    tools = await client.get_tools()
    
    # Filter tools if specified
    if filter_tools:
        if isinstance(filter_tools, str):
            # Single tool name
            tools = [tool for tool in tools if tool.name == filter_tools]
        elif isinstance(filter_tools, list):
            # List of tool names
            tools = [tool for tool in tools if tool.name in filter_tools]
    
    print(f"MCP TOOLS: Loaded {len(tools)} Instagram MCP tools via HTTP")
    return tools


# MOCK INSTAGRAM TOOLS FOR TESTING
async def setup_mock_tools():
    """Mock Instagram tools for testing the workflow"""
    from langchain_core.tools import tool
    
    @tool
    def get_user_info(username: str) -> str:
        """Get Instagram user info"""
        return f"✅ @{username}: 2.5K followers, bio: 'Sustainable tech enthusiast 🌱 | Solar energy advocate'"
    
    @tool  
    def get_user_posts(username: str, amount: int = 5) -> str:
        """Get recent posts from user"""
        return f"📱 Recent posts from @{username}:\n1. 'Just installed solar panels! #sustainabletech'\n2. 'Review of eco-friendly phone accessories'\n3. 'Why I switched to renewable energy'"
    
    @tool
    def send_message(username: str, message: str) -> str:
        """Send DM to user"""
        print(f"\n📩 SENDING DM TO @{username}:")
        print(f"💬 {message}")
        return f"✅ Message sent successfully to @{username}"
    
    return [get_user_info, get_user_posts, send_message]


# Create the three specialized agents
async def create_dm_agents():
    """Create all DM creation agents"""
    
    instagram_tools = await setup_instagram_tools()
    tools = instagram_tools
    
    profile_analyzer = create_react_agent(
        model=f"{PROVIDER}:{MODEL}",
        tools=tools,  # get_user_info, get_user_posts, etc.
        name="profile_analyzer",
        prompt=profile_analyzer_prompt
    )
    
    message_writer = create_react_agent(
        model=f"{PROVIDER}:{MODEL}", 
        tools=[],  # send_message, plus analysis tools
        name="message_writer", 
        prompt=message_writer_prompt
    )
    
    verifier = create_react_agent(
        model=f"{PROVIDER}:{MODEL}",
        tools=[],  # No Instagram tools, just verification
        name="verifier",
        prompt=verifier_prompt
    )
    
    return profile_analyzer, message_writer, verifier


async def create_dm_supervisor():
    """Create the DM creation supervisor"""
    
    profile_analyzer, message_writer, verifier = await create_dm_agents()

    send_tool = await setup_instagram_tools("send_message")
    
    dm_supervisor = create_supervisor(
        agents=[profile_analyzer, message_writer, verifier],
        tools=send_tool,
        model=ChatOpenAI(model=MODEL),
        #state_schema=CampaignState,
        prompt=supervisor_prompt,
        add_handoff_back_messages=True,
        output_mode="last_message",
    ).compile()
    
    return dm_supervisor


def pretty_print_message(message, indent=False):
    pretty_message = message.pretty_repr(html=True)
    if not indent:
        print(pretty_message)
        return
    indented = "\n".join("\t" + c for c in pretty_message.split("\n"))
    print(indented)

def pretty_print_messages(update, last_message=False):
    is_subgraph = False
    if isinstance(update, tuple):
        ns, update = update
        # skip parent graph updates in the printouts
        if len(ns) == 0:
            return
        graph_id = ns[-1].split(":")[0]
        print(f"Update from subgraph {graph_id}:")
        print("\n")
        is_subgraph = True
    
    for node_name, node_update in update.items():
        update_label = f"Update from node {node_name}:"
        if is_subgraph:
            update_label = "\t" + update_label
        print(update_label)
        print("\n")
        
        # Handle structured response nodes
        if node_name == "generate_structured_response":
            print(f"Structured Response: {node_update}")
            print("\n")
            continue
            
        # Handle regular message nodes
        if "messages" in node_update:
            messages = convert_to_messages(node_update["messages"])
            if last_message:
                messages = messages[-1:]
            for m in messages:
                pretty_print_message(m, indent=is_subgraph)
        else:
            # Handle other types of updates
            print(f"Other update: {node_update}")
        print("\n")



async def test_dm_supervisor():
    """Test the DM supervisor with sample data"""
    
    supervisor = await create_dm_supervisor()
    
    initial_state = {
        "messages": [{
            "role": "user", 
            "content": "Research @andyx_p and create a personalized sales DM about our Anime Figurine. MAKE SURE TO CUSTOMISE IT TO THEIR PROFILE, EVEN IF THEY ONLY HAVE 1 POST."
        }]
    }
    
    print("\nStarting DM supervisor workflow...\n")
    
    # Use the pretty print function with updates mode
    async for chunk in supervisor.astream(initial_state, stream_mode="updates", subgraphs=True):
        pretty_print_messages(chunk)
    
    print("\nDM Creation Complete!\n")


if __name__ == "__main__":
    asyncio.run(test_dm_supervisor())