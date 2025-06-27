from typing import List, Dict
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

MODEL = "o4-mini"
PROVIDER = "openai"

async def create_riddle_agent(tools):
    prompt = """You are an assistant that analyzes Instagram DM chat histories to detect if:
    1) A riddle was asked,
    2) The riddle was answered within 3 attempts by the user,
    3) If yes, generate an appropriate response to send back.
    
    You will receive chat messages as a list of dicts, each with 'text' and 'username'.
    Return a JSON object with keys:
    {
        "riddle_asked": true/false,
        "answered_correctly": true/false,
        "response_message": "string or empty if no response needed"
    }
    """

    agent = create_react_agent(
        model=f"{PROVIDER}:{MODEL}",
        tools=tools,
        name="riddle_analyzer",
        prompt=prompt
    )
    return agent

async def handle_riddle_conversation(insta_client, username: str, messages: List[Dict]):
    # Ensure tools are loaded on InstagramClient
    if insta_client.tools is None:
        await insta_client.initialize_tools()

    tools = insta_client.tools
    agent = await create_riddle_agent(tools)

    chat_history_text = "\n".join(f"{msg.get('username', 'user')}: {msg.get('text', '')}" for msg in messages)

    input_state = {
        "messages": [{
            "role": "user",
            "content": f"Here is the Instagram DM chat history with @{username}:\n{chat_history_text}\n\nAnalyze and respond as per instructions."
        }]
    }

    response = await agent.arun(input_state)

    import json
    try:
        result = json.loads(response)
    except Exception:
        print(f"⚠️ Failed to parse agent response as JSON: {response}")
        return

    if result.get("riddle_asked") and result.get("answered_correctly") and result.get("response_message"):
        reply = result["response_message"]
        print(f"📩 Sending riddle reply to @{username}: {reply}")
        await insta_client.send_message(username, reply)
    else:
        print(f"ℹ️ No riddle response needed for @{username}")
