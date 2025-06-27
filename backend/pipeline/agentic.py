import asyncio
import os
from typing import Dict, Any, List
from langgraph_supervisor import create_supervisor
from langgraph.prebuilt import create_react_agent
from langgraph.graph import MessagesState
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langchain_core.messages import convert_to_messages


class CampaignState(MessagesState):
    product: Dict[str, Any] = {}
    current_username: str = ""
    profile_analysis: Dict[str, Any] = {}
    draft_message: str = ""
    verification_result: Dict[str, Any] = {}
    
    remaining_steps: int = 10
    is_last_step: bool = False



async def setup_instagram_tools():
    """Setup MCP client to get Instagram tools via HTTP"""
    
    client = MultiServerMCPClient({
        "instagram_dm": {
            "url": "http://localhost:8000/mcp",
            "transport": "streamable_http",
        }
    })
    
    tools = await client.get_tools()
    print(f"✅ Loaded {len(tools)} Instagram MCP tools via HTTP")
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
        model="openai:gpt-4o",
        tools=tools,  # get_user_info, get_user_posts, etc.
        name="profile_analyzer",
        prompt="You analyze Instagram profiles to understand users' interests and content style." \
        "Use the instagram MCP tools that you have available to you to collect info. " \
        "DO NOT send any messages or use tools that are not relevant to that specific task. You are just collecting context to be passed on."
    )
    
    message_writer = create_react_agent(
        model="openai:gpt-4o", 
        tools=[],  # send_message, plus analysis tools
        name="message_writer", 
        prompt="You write personalized DMs based on profile analysis and product info. " \
        "Given the context you got about a user, write a DM to advertise the product." \
        "DO NOT SEND IT, just return it."
    )
    
    verifier = create_react_agent(
        model="openai:gpt-4o",
        tools=[],  # No Instagram tools, just verification
        name="verifier",
        prompt="You verify DM quality - is it personalized, appropriate, and compelling? Answer with your assessment."
    )
    
    return profile_analyzer, message_writer, verifier



supervisor_prompt = """You coordinate Instagram DM creation. Process:
        1. Have profile_analyzer research the target user
        2. Have message_writer create personalized DM based on analysis, being sure to GIVE IT the context that you got from profile_analyzer. 
        3. Have verifier check message quality
        4. If verification fails, coordinate improvements (being sure to pass any feedback to sub-agents you call)
        Finish once you have a crafted, verified DM. Return that DM."""

test_prompt = """
Tell me a joke. do nothing else.
"""

async def create_dm_supervisor():
    """Create the DM creation supervisor"""
    
    profile_analyzer, message_writer, verifier = await create_dm_agents()
    
    dm_supervisor = create_supervisor(
        agents=[profile_analyzer, message_writer, verifier],
        model=ChatOpenAI(model="gpt-4"),
        #state_schema=CampaignState,
        prompt=supervisor_prompt,
        add_handoff_back_messages=True,
        output_mode="full_history",
    ).compile()
    
    return dm_supervisor



from langchain_core.messages import convert_to_messages

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
        
        messages = convert_to_messages(node_update["messages"])
        if last_message:
            messages = messages[-1:]
        for m in messages:
            pretty_print_message(m, indent=is_subgraph)
        print("\n")

async def test_dm_supervisor():
    """Test the DM supervisor with sample data"""
    
    supervisor = await create_dm_supervisor()
    
    initial_state = {
        "messages": [{
            "role": "user", 
            "content": "Research @andyx_p and create a personalized DM about our Anime Figurine. MAKE SURE TO CUSTOMISE IT TO THEIR PROFILE, EVEN IF THEY ONLY HAVE 1 POST."
        }]
    }
    
    print("🚀 Starting DM supervisor workflow...")
    
    # Use the pretty print function with updates mode
    async for chunk in supervisor.astream(initial_state, stream_mode="updates", subgraphs=True):
        pretty_print_messages(chunk)
    
    print("✅ DM Creation Complete!")



if __name__ == "__main__":
    asyncio.run(test_dm_supervisor())