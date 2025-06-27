import operator
from typing import Annotated, List, Dict
from typing_extensions import TypedDict
from pydantic import BaseModel, Field

from langchain_openai import ChatOpenAI
from langgraph.types import Send
from langgraph.graph import StateGraph, START, END
from langchain_community.document_loaders import WebBaseLoader

from dm_creation_pipeline import create_dm_supervisor, pretty_print_messages
from user_finding_pipeline import create_user_finder_agent


MODEL = "o4-mini"
PROVIDER = "openai"

llm = ChatOpenAI(model=MODEL)




# Pydantic model for user finder structured output 
class DiscoveredUsers(BaseModel):
    usernames: List[str] = Field(description="List of discovered Instagram usernames")

class ProductPayload(TypedDict):
    title: str
    category: str
    price: str
    link: str 

# Overall campaign state (main graph state)
class CampaignState(TypedDict):
    product_payload: ProductPayload
    product_info: str
    discovered_users: List[str]  # From user finder
    dm_results: Annotated[List[str], operator.add]  # Collected DM results (reduce step)
    campaign_summary: str

# Individual DM creation state (sent to each dm_creation_node)
class DMState(TypedDict):
    username: str
    product_info: str




# NODE FUNCTIONS

async def product_info_scraper(state: CampaignState):
    """Generate a formatted product description from the product URL"""
    payload = state["product_payload"]
    
    try:
        # Load the webpage content
        loader = WebBaseLoader(
            web_path=payload["link"],
            bs_get_text_kwargs={"separator": " ", "strip": True},
            continue_on_failure=True  # Don't crash if URL fails
        )
        
        # Use async loading
        docs = []
        async for doc in loader.alazy_load():
            docs.append(doc)
        
        if not docs:
            # Fallback if scraping fails
            product_info = f"Product: {payload['title']} - {payload['category']} - ${payload['price']}"
        else:
            # Extract content and create LLM-formatted description
            raw_content = docs[0].page_content[:3000]  # Limit to avoid token limits
            
            formatting_prompt = f"""
            Create a concise, engaging product description based on this scraped content and product details:
            
            Product Title: {payload['title']}
            Category: {payload['category']} 
            Price: ${payload['price']}
            
            Scraped Content: {raw_content}
            
            Generate a paragraph product description of this item, including the most relevant details about it. Make it at least 3 sentences.
            Include a title and price above the description too, but output all as one string.
            """
            
            response = await llm.ainvoke(formatting_prompt)
            product_info = response.content.strip()

    
    except Exception as e:
        # Fallback if anything fails
        product_info = f"High-quality {payload['category']}: {payload['title']} - Available for ${payload['price']}. Perfect for enthusiasts and collectors."
        print(f"Scraping failed, using fallback: {e}")
    
    print(product_info)
    return {"product_info": product_info}



async def user_finder_node(state: CampaignState):
    """User finder agent - assume it returns structured output"""
    user_finder = create_user_finder_agent()  # REMOVED await
    input = {"messages": [{"role": "user", "content": f"Find users for {state['product_info']}"}]}
    
    result = await user_finder.ainvoke(input)
    # async for chunk in user_finder.astream(input, stream_mode="updates", subgraphs=True):
    #     # pretty_print_messages(chunk)
    
    return {"discovered_users": result["structured_response"].usernames}


async def dm_creation_node(state: DMState):
    """Wrapper node that creates fresh DM supervisor for each user"""
    
    # Create fresh supervisor instance for isolation
    dm_supervisor = await create_dm_supervisor()  # REMOVED await
    
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
    graph.add_node("product_info_scraper", product_info_scraper)
    graph.add_node("user_finder", user_finder_node)
    graph.add_node("dm_creation", dm_creation_node)  # This gets called multiple times via Send
    graph.add_node("campaign_summary", create_campaign_summary)
    
    # Add edges
    graph.add_edge(START, "product_info_scraper")
    graph.add_edge("product_info_scraper", "user_finder")
    
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
async def run_instagram_campaign(product_payload: ProductPayload):
    """Run the complete Instagram campaign with map-reduce"""
    
    # Create graph
    campaign_graph = await create_campaign_graph()
    
    # Initial state
    initial_state = {
        "product_payload": product_payload,
        "product_info": "",
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
    
    product_info = """
Dragon Ball Z S.H. Figuarts Super Saiyan Son Goku “The Games Begin” Ver. – 15 cm

Experience the power of the Cell Saga with Super Saiyan Son Goku in Bandai Tamashii Nations’ latest S.H. Figuarts release. This fully articulated figure features all-new modeling, capturing Goku’s iconic proportions, voluminous spiky hair, and intense facial expressions straight from the anime. Built on the upgraded movable structure refined across the Dragon Ball S.H. Figuarts line, it stands approximately 15 cm tall and comes complete with interchangeable hands and accessories, beautifully presented in a window display box.

Part of the official S.H. Figuarts series, this collector’s item is available for preorder now at £29.95 (or a £4.95 deposit option). Estimated delivery is mid-January 2026. Enjoy free UK shipping, with European and international shipping options also available.

Safety & Age Recommendation:
This is a collector’s item, not a toy. Contains small parts—choking hazard. Recommended for ages 14 and up.
"""

    fake_product_payload = {
        "title": "Dragon Ball Z, S.H. Figuarts Action Figure -- Super Saiyan Son Goku The Games Begin Ver. 15cm",
        "category": "Collectibles & Figurines", 
        "price": "29.99",
        "link": "https://hobbyfigures.co.uk/collections/anime/products/dragon-ball-z-s-h-figuarts-action-figure-super-saiyan-son-goku-the-games-begin-ver-15cm"
    }

    
    asyncio.run(run_instagram_campaign(fake_product_payload))