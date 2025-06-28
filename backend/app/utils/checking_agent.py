import asyncio
from typing import List, Optional, Union
from pydantic import BaseModel

# Simple imports first
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

# Import the exact components from the documentation
from langgraph.graph import StateGraph, START, END, MessagesState

import asyncio
from typing import List, Optional, Union
from pydantic import BaseModel

# Check LangGraph version first
try:
    import langgraph
    print(f"📦 LangGraph version: {langgraph.__version__}")
except:
    print("📦 LangGraph version: unknown")

# Simple imports first
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

# Import the exact components from the documentation
from langgraph.graph import StateGraph, START, END, MessagesState

# Try different import locations for Send
HAS_SEND = False
Send = None

# Based on the documentation, Send is in langgraph.types!
try:
    from langgraph.types import Send
    print("✅ Send import successful from langgraph.types")
    HAS_SEND = True
except ImportError:
    try:
        from langgraph.graph import Send
        print("✅ Send import successful from langgraph.graph")
        HAS_SEND = True
    except ImportError:
        print("❌ Send not found in any location")
        print("💡 Let's check what's available...")
        
        # Debug: show what's available
        try:
            import langgraph.types
            types_available = [attr for attr in dir(langgraph.types) if not attr.startswith('_')]
            print(f"Available in langgraph.types: {types_available}")
        except ImportError:
            print("langgraph.types module not available")
            
        try:
            import langgraph.graph
            graph_available = [attr for attr in dir(langgraph.graph) if not attr.startswith('_')]
            print(f"Available in langgraph.graph: {graph_available}")
        except ImportError:
            print("langgraph.graph module not available")

# Import prompts
from app.utils.reply_agent_prompts import (
    username_extractor_prompt, 
    individual_reply_agent_prompt
)

MODEL = "o4-mini"
PROVIDER = "openai"

class ChatContext(BaseModel):
    username: str
    chat_history: Union[str, List[str]]

# Simple state class extending MessagesState as shown in docs
class ReplyState(MessagesState):
    pass

async def setup_instagram_tools():
    """Setup MCP client to get Instagram tools via HTTP"""
    client = MultiServerMCPClient({
        "instagram_dm": {
            "url": "http://localhost:8000/mcp",
            "transport": "streamable_http",
        }
    })
    tools = await client.get_tools()
    print(f"MCP TOOLS: Loaded {len(tools)} Instagram MCP tools via HTTP")
    return tools

async def create_username_extractor_agent():
    """Create the username extractor agent"""
    tools = await setup_instagram_tools()
    extractor_tools = [tool for tool in tools if tool.name in ["list_chats", "list_messages"]]
    
    return create_react_agent(
        model=f"{PROVIDER}:{MODEL}",
        tools=extractor_tools,
        name="username_extractor",
        prompt=username_extractor_prompt
    )

def parse_users_from_extractor_output(extractor_output: str) -> List[ChatContext]:
    """Parse the username extractor output to get users needing replies"""
    users_needing_replies = []
    
    # Convert to lowercase for easier parsing
    output_lower = extractor_output.lower()
    
    # Check if explicitly says no users need replies
    if "no_users_need_replies" in output_lower or "no replies needed" in output_lower:
        return []
    
    # Parse the extractor output
    lines = extractor_output.split('\n')
    
    current_username = None
    current_chat_history = []
    
    for line in lines:
        line = line.strip()
        
        # Look for username patterns like "@username:" or "username:"
        if '@' in line and ':' in line:
            # Save previous user if exists
            if current_username and current_chat_history:
                users_needing_replies.append(ChatContext(
                    username=current_username,
                    chat_history='\n'.join(current_chat_history)
                ))
            
            # Extract username
            username_part = line.split(':')[0]
            username_part = username_part.replace('-', '').replace('*', '').replace('@', '').strip()
            
            if username_part:
                current_username = username_part
                current_chat_history = [line.split(':', 1)[1].strip()] if ':' in line else []
            
        elif current_username and line and not line.startswith('USERS_NEEDING_REPLIES'):
            current_chat_history.append(line)
    
    # Don't forget the last user
    if current_username and current_chat_history:
        users_needing_replies.append(ChatContext(
            username=current_username,
            chat_history='\n'.join(current_chat_history)
        ))
    
    return users_needing_replies

# The Send routing function - exactly as shown in documentation
def continue_to_replies(state: ReplyState):
    """
    This function returns Send objects to spawn concurrent reply agents
    Exactly like the documentation example: 
    >>> from langgraph.types import Send
    >>> def continue_to_jokes(state: OverallState):
    ...     return [Send("generate_joke", {"subject": s}) for s in state['subjects']]
    """
    if not state.get("messages"):
        return []
    
    last_message = state["messages"][-1].content
    users_waiting_for_reply = parse_users_from_extractor_output(last_message)
    
    print(f"\n🚀 Found {len(users_waiting_for_reply)} users needing replies")
    
    if not HAS_SEND:
        print("⚠️ Send not available - using fallback")
        return "__end__" if not users_waiting_for_reply else "reply_to_dm"
    
    print(f"🚀 Using Send pattern for {len(users_waiting_for_reply)} concurrent replies")
    
    # This is the exact pattern from the documentation!
    # return [Send("generate_joke", {"subject": s}) for s in state['subjects']]
    return [Send("reply_to_dm", {"chat_context": chat_context}) for chat_context in users_waiting_for_reply]

async def reply_to_dm_node(state):
    """
    Individual node to handle one DM reply - gets called concurrently via Send
    """
    chat_context = state.get("chat_context")
    if not chat_context:
        return {"messages": []}
    
    print(f"\n🔄 Processing reply for @{chat_context.username}")
    
    # Use real Instagram tools
    tools = await setup_instagram_tools()
    reply_tools = [tool for tool in tools if tool.name in ["get_user_info", "send_message"]]
    
    individual_reply_agent = create_react_agent(
        model=f"{PROVIDER}:{MODEL}",
        tools=reply_tools,
        name=f"reply_agent_{chat_context.username}",
        prompt=individual_reply_agent_prompt
    )
    
    agent_state = {
        "messages": [{
            "role": "user",
            "content": f"Create and send a personalized reply to @{chat_context.username}.\n\nChat History:\n{chat_context.chat_history}\n\nAnalyze their profile, craft an appropriate response, and send it."
        }]
    }
    
    result = await individual_reply_agent.ainvoke(agent_state)
    return {"messages": result.get("messages", [])}

async def create_send_pattern_graph():
    """Create the graph using Send pattern for concurrent processing"""
    
    # Create the username extractor
    username_extractor = await create_username_extractor_agent()
    
    # Create the state graph - exactly as shown in documentation
    builder = StateGraph(ReplyState)
    
    # Add nodes
    builder.add_node("username_extractor", username_extractor)
    builder.add_node("reply_to_dm", reply_to_dm_node)
    
    # Define the workflow - exactly as shown in documentation
    builder.add_edge(START, "username_extractor")
    builder.add_conditional_edges("username_extractor", continue_to_replies)
    builder.add_edge("reply_to_dm", END)
    
    return builder.compile()

async def test_send_pattern():
    """Test the Send pattern for concurrent replies"""
    
    print(f"\n🧪 Testing Send Pattern (Available: {HAS_SEND})")
    
    if not HAS_SEND:
        print("\n💡 Send pattern not available. To use Send pattern:")
        print("   1. Check your LangGraph version:")
        print("      pip show langgraph")
        print("   2. Upgrade if needed:")
        print("      pip install --upgrade langgraph")
        print("   3. LangGraph Send was introduced in version 0.1.0+")
        print("\n⚙️ Using alternative concurrent approach with asyncio.gather...")
        
        # Alternative: Use asyncio.gather for true concurrency
        await test_asyncio_concurrent_approach()
        return
    
    try:
        # Create the graph
        graph = await create_send_pattern_graph()
        
        initial_state = {
            "messages": [{
                "role": "user", 
                "content": "Check for any DMs that need replies and process them using Send pattern. Use the list_chats and list_messages tools to get real Instagram data."
            }]
        }
        
        print("\n📋 Executing Send pattern workflow...")
        
        # Stream the execution
        results = []
        async for chunk in graph.astream(initial_state, stream_mode="updates"):
            print(f"\n🔍 Step: {list(chunk.keys())}")
            
            # Collect results from concurrent reply nodes
            for node_name, node_data in chunk.items():
                if node_name == "reply_to_dm":
                    results.append(f"✅ Completed reply via Send pattern")
        
        if results:
            print(f"\n🎉 Send pattern results: {len(results)} concurrent replies completed")
        else:
            print("\n💡 No users needed replies")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

async def test_asyncio_concurrent_approach():
    """Alternative: Use asyncio.gather for true concurrency"""
    
    print("\n🚀 Using asyncio.gather for concurrent processing...")
    
    # Step 1: Extract users needing replies
    username_extractor = await create_username_extractor_agent()
    
    initial_state = {
        "messages": [{
            "role": "user", 
            "content": "Check for any DMs that need replies and extract usernames with chat history. Use the list_chats and list_messages tools to get real Instagram data."
        }]
    }
    
    extractor_result = await username_extractor.ainvoke(initial_state)
    last_message = extractor_result["messages"][-1].content
    
    # Step 2: Parse users
    users_waiting_for_reply = parse_users_from_extractor_output(last_message)
    
    if not users_waiting_for_reply:
        print("💡 No users need replies")
        return
    
    print(f"✅ Found {len(users_waiting_for_reply)} users needing replies: {[u.username for u in users_waiting_for_reply]}")
    
    # Step 3: Process all users concurrently using asyncio.gather
    async def process_single_user(chat_context: ChatContext):
        """Process a single user's reply"""
        print(f"\n🔄 Processing reply for @{chat_context.username}")
        
        tools = await setup_instagram_tools()
        reply_tools = [tool for tool in tools if tool.name in ["get_user_info", "send_message"]]
        
        individual_reply_agent = create_react_agent(
            model=f"{PROVIDER}:{MODEL}",
            tools=reply_tools,
            name=f"reply_agent_{chat_context.username}",
            prompt=individual_reply_agent_prompt
        )
        
        agent_state = {
            "messages": [{
                "role": "user",
                "content": f"Create and send a personalized reply to @{chat_context.username}.\n\nChat History:\n{chat_context.chat_history}\n\nAnalyze their profile, craft an appropriate response, and send it."
            }]
        }
        
        result = await individual_reply_agent.ainvoke(agent_state)
        return {"username": chat_context.username, "status": "reply_sent"}
    
    print(f"\n⚡ Processing {len(users_waiting_for_reply)} replies concurrently with asyncio.gather...")
    
    # This achieves the same concurrent processing as Send pattern!
    tasks = [process_single_user(user) for user in users_waiting_for_reply]
    results = await asyncio.gather(*tasks)
    
    print(f"\n🎉 Asyncio concurrent replies completed for: {[r['username'] for r in results]}")
    return results

if __name__ == "__main__":
    asyncio.run(test_send_pattern())