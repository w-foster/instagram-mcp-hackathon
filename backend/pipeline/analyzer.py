import asyncio
import os
from typing import Dict, Any
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph, MessagesState, START, END
from langchain_openai import ChatOpenAI

# Define state for our profile analyzer
class ProfileAnalysisState(MessagesState):
    username: str = ""
    product_context: Dict[str, Any] = {}
    analysis_result: Dict[str, Any] = {}

async def setup_instagram_tools():
    """Setup MCP client to get Instagram tools"""
    # Following LangGraph MCP docs pattern exactly
    client = MultiServerMCPClient({
        "instagram_dms": {
            "command": "python",
            "args": ["/path/to/your/instagram_dm_mcp/src/mcp_server.py"],  # Update this path
            "transport": "stdio",
        }
    })
    
    # Get all tools from MCP server
    tools = await client.get_tools()
    
    # Filter to analysis-relevant tools only
    analysis_tools = [tool for tool in tools if tool.name in [
        'get_user_info',
        'get_user_posts', 
        'get_user_followers',
        'get_user_following',
        'get_user_stories'
    ]]
    
    print(f"✅ Loaded {len(analysis_tools)} Instagram analysis tools")
    return analysis_tools

def create_analysis_prompt_node(state: ProfileAnalysisState) -> ProfileAnalysisState:
    """Node function to create the analysis prompt"""
    username = state.get("username", "")
    product = state.get("product_context", {})
    
    analysis_prompt = f"""
    Analyze Instagram profile "@{username}" for potential outreach about our product:
    
    Product: {product.get('name', 'N/A')} - {product.get('description', 'N/A')}
    Price: {product.get('price', 'N/A')}
    
    Please thoroughly research this user:
    1. Get their basic profile info (followers, bio, etc.)
    2. Analyze their recent posts (5-10 posts)
    3. Look for interests that align with our product
    4. Assess if they're a good outreach target
    5. Note any personalization opportunities
    
    Provide a comprehensive analysis with specific examples from their content.
    """
    
    return {
        "messages": [{"role": "user", "content": analysis_prompt}]
    }

def extract_analysis_result(state: ProfileAnalysisState) -> ProfileAnalysisState:
    """Node function to extract and structure the analysis result"""
    # Get the last AI message which contains the analysis
    last_message = state["messages"][-1].content if state["messages"] else ""
    
    analysis_result = {
        "username": state.get("username", ""),
        "analysis": last_message,
        "status": "completed"
    }
    
    return {"analysis_result": analysis_result}

async def create_profile_analyzer_graph():
    """Create the complete profile analyzer graph"""
    
    # Get Instagram tools from MCP
    instagram_tools = await setup_instagram_tools()
    
    # Create the React agent for Instagram analysis
    # This follows the exact pattern from LangGraph docs
    analyzer_agent = create_react_agent(
        model="openai:gpt-4",
        tools=instagram_tools,
        prompt="""You are an expert Instagram profile analyzer. 
        Use the available Instagram tools to thoroughly research users.
        Always start with get_user_info, then get_user_posts, and use other tools as needed.
        Provide detailed analysis of their content, interests, and outreach potential.""",
        name="instagram_analyzer"
    )
    
    # Create the StateGraph - this is the proper LangGraph way
    builder = StateGraph(ProfileAnalysisState)
    
    # Add nodes to the graph
    builder.add_node("create_prompt", create_analysis_prompt_node)
    builder.add_node("analyze", analyzer_agent)  # The React agent as a node
    builder.add_node("extract_result", extract_analysis_result)
    
    # Add edges to define the flow
    builder.add_edge(START, "create_prompt")
    builder.add_edge("create_prompt", "analyze") 
    builder.add_edge("analyze", "extract_result")
    builder.add_edge("extract_result", END)
    
    # Compile the graph - THIS IS REQUIRED
    graph = builder.compile()
    
    return graph

# Usage example
async def analyze_profile(username: str, product_context: Dict[str, Any]):
    """Main function to analyze a profile"""
    
    # Create the graph
    graph = await create_profile_analyzer_graph()
    
    # Initial state
    initial_state = {
        "username": username,
        "product_context": product_context,
        "messages": []
    }
    
    # Invoke the graph - this runs the entire flow
    result = await graph.ainvoke(initial_state)
    
    return result["analysis_result"]

# Test the analyzer
async def test_analyzer():
    os.environ["OPENAI_API_KEY"] = "your-api-key"
    
    product = {
        "name": "Eco Phone Case",
        "description": "Sustainable phone case made from recycled materials",
        "price": "$24.99"
    }
    
    # This will run: create_prompt -> analyze (React agent) -> extract_result
    result = await analyze_profile("test_username", product)
    print(f"Analysis result: {result}")

if __name__ == "__main__":
    asyncio.run(test_analyzer())