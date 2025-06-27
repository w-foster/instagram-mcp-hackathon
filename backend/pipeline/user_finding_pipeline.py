import asyncio
import os
from typing import Dict, Any, List
from langgraph_supervisor import create_supervisor
from langgraph.prebuilt import create_react_agent
from langgraph.graph import MessagesState
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langchain_core.messages import convert_to_messages, tool
from pydantic import BaseModel


@tool
def extract_hashtags(product_info: str, context: str = "") -> str:
    """
    Extract relevant hashtags for a product to find Instagram users.
    
    Args:
        product_info: Product description, title, and details
        context: Previous attempts and feedback (what worked/didn't work)
    """
    prompt = f"""
    Product: {product_info}
    
    Context from previous attempts: {context}
    
    Based on the context, generate 5-10 relevant Instagram hashtags.
    - If previous hashtags were "too broad" (found too many users), be more specific
    - If previous hashtags were "too specific" (found too few users), be broader
    - If no context, start with medium-specificity hashtags
    
    Return only hashtags separated by commas, without # symbols.
    """
    
    response = hashtag_llm.invoke(prompt)
    return response.content.strip()

@tool 
def find_instagram_users(hashtags: str) -> str:
    """Find Instagram usernames who posted with given hashtags."""
    hashtag_list = [tag.strip() for tag in hashtags.split(",")]
    users = fetch_hashtag_usernames(
        hashtags=hashtag_list,
        max_posts=10,
        username="instamcp2", 
        password="Password1."
    )
    
    # Provide rich feedback for the agent to reason about
    user_count = len(users)
    if user_count < 5:
        return f"Found only {user_count} users with hashtags '{hashtags}'. These hashtags might be too specific or niche."
    elif user_count > 100:
        return f"Found {user_count} users with hashtags '{hashtags}'. These hashtags might be too broad - consider more specific ones."
    else:
        return f"Found {user_count} users with hashtags '{hashtags}': {', '.join(list(users)[:15])}{'...' if user_count > 15 else ''}"

# Enhanced agent prompt
user_finder_agent = create_react_agent(
    model="openai:gpt-4-turbo",
    tools=[extract_hashtags, find_instagram_users],
    name="user_finder",
    prompt="""You find Instagram users for marketing campaigns. 

Your process:
1. Use extract_hashtags to get relevant hashtags for the product
2. Use find_instagram_users to discover potential customers
3. Analyze the results:
   - If too few users (< 10): Extract broader/different hashtags
   - If too many users (> 50): Extract more specific hashtags  
   - If good amount (10-50): You're done!

Keep track of what you've tried and learn from the feedback. When calling extract_hashtags again, pass context about what happened before so it can adjust strategy.

Goal: Find 15-40 relevant potential customers."""
)