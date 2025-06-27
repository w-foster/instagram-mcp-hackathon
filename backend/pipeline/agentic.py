import operator
from typing import Annotated, List
from typing_extensions import TypedDict
from pydantic import BaseModel, Field

from langgraph.types import Send
from langgraph.graph import StateGraph, START, END

from dm_creation_pipeline import create_dm_supervisor, pretty_print_messages
from user_finding_pipeline import create_user_finder_agent


# Pydantic model for user finder structured output (assume this exists)
class DiscoveredUsers(BaseModel):
    usernames: List[str] = Field(description="List of discovered Instagram usernames")

# Overall campaign state (main graph state)
class CampaignState(TypedDict):
    product_info: str
    discovered_users: List[str]  # From user finder
    dm_results: Annotated[List[str], operator.add]  # Collected DM results (reduce step)
    campaign_summary: str

# Individual DM creation state (sent to each dm_creation_node)
class DMState(TypedDict):
    username: str
    product_info: str




# Node functions

async def user_finder_node(state: CampaignState):
    """User finder agent - assume it returns structured output"""
    user_finder = create_user_finder_agent()  # REMOVED await
    input = {"messages": [{"role": "user", "content": f"Find users for {state['product_info']}"}]}
    
    result = await user_finder.ainvoke(input)
    # async for chunk in user_finder.astream(input, stream_mode="updates", subgraphs=True):
    #     # pretty_print_messages(chunk)
    
    return {"discovered_users": result["structured_response"]}


async def dm_creation_node(state: DMState):
    """Wrapper node that creates fresh DM supervisor for each user"""
    
    # Create fresh supervisor instance for isolation
    dm_supervisor = create_dm_supervisor()  # REMOVED await
    
    username = state["username"]
    product_info = state["product_info"]
    
    try:
        # Create input for DM supervisor
        dm_input = {
            "messages": [{
                "role": "user", 
                "content": f"Research @{username} and create a personalized sales DM about {product_info}. Customise it to their profile."
            }]
        }
        
        # Run the DM supervisor
        result = await dm_supervisor.ainvoke(dm_input)
        # async for chunk in dm_supervisor.astream(dm_input, stream_mode="updates", subgraphs=True):
        #     pretty_print_messages(chunk)
        
        # Extract the final DM from the supervisor result
        last_message = result["messages"][-1]
        dm_content = last_message.content if hasattr(last_message, 'content') else str(last_message)
        
        # Return success result
        return {"dm_results": [f"SUCCESS: @{username}: {dm_content[:100]}..."]}
        
    except Exception as e:
        # Return failure result
        return {"dm_results": [f"FAIL: @{username}: Failed - {str(e)}"]}



async def create_campaign_summary(state: CampaignState):
    """Reduce step - summarize all DM creation results"""
    dm_results = state["dm_results"]
    total_users = len(state["discovered_users"])
    successful_dms = len([r for r in dm_results if r.startswith("✅")])
    failed_dms = len([r for r in dm_results if r.startswith("❌")])
    
    summary = f"""
Instagram Campaign Complete!

Results Summary:
• Total Users Discovered: {total_users}
• Successful DMs Created: {successful_dms}
• Failed DM Attempts: {failed_dms}
• Success Rate: {(successful_dms/total_users)*100:.1f}%

Individual Results:
{chr(10).join(dm_results)}

Campaign Status: {'SUCCESS' if successful_dms > 0 else 'NEEDS REVIEW'}
    """
    
    return {"campaign_summary": summary}



# Mapping function for Send API 
async def continue_to_dm_creation(state: CampaignState):
    """Map discovered users to parallel DM creation tasks"""
    discovered_users = state["discovered_users"]
    product_info = state["product_info"]
    
    # Create Send object for each user (mapping out)
    return [Send("dm_creation", {
        "username": username,
        "product_info": product_info
    }) for username in discovered_users]




# Build the complete campaign graph
async def create_campaign_graph():
    """Create the Instagram campaign graph with map-reduce pattern"""
    
    # Initialize graph
    graph = StateGraph(CampaignState)
    
    # Add nodes
    graph.add_node("user_finder", user_finder_node)
    graph.add_node("dm_creation", dm_creation_node)  # This gets called multiple times via Send
    graph.add_node("campaign_summary", create_campaign_summary)
    
    # Add edges
    graph.add_edge(START, "user_finder")
    
    # Key part: conditional edge with Send API for map-reduce
    graph.add_conditional_edges(
        "user_finder", 
        continue_to_dm_creation,  # This function returns list of Send objects
        ["dm_creation"]  # Target nodes for the Send objects
    )
    
    # Reduce step - all dm_creation nodes flow to summary
    graph.add_edge("dm_creation", "campaign_summary")
    graph.add_edge("campaign_summary", END)
    

    # Compile graph
    return graph.compile()


# Main execution function
async def run_instagram_campaign(product_info: str):
    """Run the complete Instagram campaign with map-reduce"""
    
    # Create graph
    campaign_graph = await create_campaign_graph()
    
    # Initial state
    initial_state = {
        "product_info": product_info,
        "discovered_users": [],
        "dm_results": [],
        "campaign_summary": ""
    }
    
    print("Starting Instagram Campaign...")
    print(f"Product: {product_info}")
    print("\n" + "="*60 + "\n")
    
    # Execute campaign
    async for chunk in campaign_graph.astream(initial_state, stream_mode="updates", subgraphs=True):
        pretty_print_messages(chunk)
    
    

# Example usage
if __name__ == "__main__":
    import asyncio
    
    product_info = "Premium Anime Figurine Collection - High-quality collectible figures"
    asyncio.run(run_instagram_campaign(product_info))