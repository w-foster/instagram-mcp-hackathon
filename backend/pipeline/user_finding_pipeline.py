import asyncio
import os
from typing import Dict, Any, List
from langgraph.prebuilt import create_react_agent
from langgraph.graph import MessagesState
from langchain_openai import ChatOpenAI
from langchain_core.messages import convert_to_messages
from langchain_core.tools import tool
from pydantic import BaseModel

from get_tags import fetch_hashtag_usernames

MODEL = "o4-mini"
PROVIDER = "openai"

hashtag_llm = ChatOpenAI(model=MODEL)


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
    
    Return only hashtags separated by commas, WITHOUT # (hashtag) symbols.
    """
    
    response = hashtag_llm.invoke(prompt)
    return response.content.strip()

@tool 
def find_instagram_users(hashtags: str) -> str:
    """Find Instagram usernames who posted with given hashtags.
    
    Args:
        hashtags: Comma separated string of hashtags (WITHOUT # symbol)
    """
    hashtag_list = [tag.strip() for tag in hashtags.split(",")]
    users = fetch_hashtag_usernames(
        hashtags=hashtag_list,
        max_posts=10,
        username="instamcp2", 
        password="Password1."
    )
    
    # Provide rich feedback for the agent to reason about
    user_count = len(users)
    # if user_count < 10:
    #     return f"Found only {user_count} users with hashtags '{hashtags}'. These hashtags might be too specific or niche. \nUsers found: {users}"
    # elif user_count > 100:
    #     return f"Found {user_count} users with hashtags '{hashtags}'. These hashtags might be too broad - consider more specific ones. \nUsers found: {users}"

    return f"Found {user_count} users with hashtags '{hashtags}': {', '.join(list(users)[:15])}{'...' if user_count > 15 else ''}. "


class FoundUsers(BaseModel):
    usernames: List[str]


def create_user_finder_agent():
    # Enhanced agent prompt
    user_finder_agent = create_react_agent(
        model=f"{PROVIDER}:{MODEL}",
        tools=[extract_hashtags, find_instagram_users],
        name="user_finder",
        response_format=FoundUsers,
        prompt="""You find Instagram users for marketing campaigns. 

Your process:
1. Use extract_hashtags to get relevant hashtags for the product
2. Use find_instagram_users to discover potential customers
3. Analyze the results. You need to consider whether or not the hashtags are too broad or specific, or just right, based on how many users are returned. 
But you need to make this analysis IN THE CONTEXT of the product in question. For example, a more niche product demands more niche hashtags, even if not many users are found.
Whereas a very wide-appeal product can afford to have more broad hashtags.

Keep track of what you've tried and learn from the feedback. When calling extract_hashtags again, pass plenty of context about what happened before so it can adjust strategy.

Goal: Find 5 relevant potential customers. DO NOT go back and forth between your tools more than 3 times; if you still believe you have too many or too little after third, just stop anyway and return 5 usernames (or less, if you have <5)"""
    )

    return user_finder_agent