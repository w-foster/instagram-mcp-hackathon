import asyncio
from typing import Dict, Any, List
from pydantic import BaseModel
from langchain_core.tools import tool
from langgraph_supervisor import create_supervisor
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_core.messages import convert_to_messages

from app.services.instagram_client import InstagramClient

MODEL = "o4-mini"
PROVIDER = "openai"

# Define your state model if needed (optional)
class DMResult(BaseModel):
    final_dm: str
    target_user: str
    verification_status: str


async def setup_instagram_tools() -> List:
    insta_client = InstagramClient()
    await insta_client.initialize_tools()

    @tool
    async def list_pending_chats(amount: int = 20) -> Dict[str, Any]:
        try:
            threads = await insta_client.list_pending_chats(amount)
            return {"success": True, "threads": threads.get("threads", [])}
        except Exception as e:
            return {"success": False, "message": str(e)}

    @tool
    async def list_messages(thread_id: str, amount: int = 20) -> Dict[str, Any]:
        if not thread_id:
            return {"success": False, "message": "Thread ID must be provided."}
        try:
            messages = await insta_client.list_messages(thread_id, amount)
            return {"success": True, "messages": messages.get("messages", [])}
        except Exception as e:
            return {"success": False, "message": str(e)}

    @tool
    async def send_message(username: str, message: str) -> str:
        try:
            resp = await insta_client.send_message(username, message)
            return resp
        except Exception as e:
            return f"❌ Failed to send message: {e}"

    # Optionally add other tools like get_user_info, get_user_posts if needed here

    return [list_pending_chats, list_messages, send_message]


async def create_dm_agents(tools):
    profile_analyzer = create_react_agent(
        model=f"{PROVIDER}:{MODEL}",
        tools=tools,
        name="profile_analyzer",
        prompt=(
            "You analyze Instagram profiles to understand users' interests and content style. "
            "You are NOT writing the DM itself, just gathering context which will be passed on to a Writer. "
            "Use the Instagram MCP tools to collect info about the target user. "
            "DO NOT send any messages or perform unrelated actions."
        )
    )

    message_writer = create_react_agent(
        model=f"{PROVIDER}:{MODEL}",
        tools=[],
        name="message_writer",
        prompt=(
            "You write personalized DMs based on profile analysis and product info. "
            "Given the context you received about a user, write a DM advertising the product. "
            "DO NOT SEND IT, just return the DM text."
        )
    )

    verifier = create_react_agent(
        model=f"{PROVIDER}:{MODEL}",
        tools=[],
        name="verifier",
        prompt=(
            "You verify DM quality. Check if it is personalized, appropriate, and compelling. "
            "Answer with your assessment only."
        )
    )

    return profile_analyzer, message_writer, verifier


supervisor_prompt = """
You are a supervisor agent coordinating Instagram DM creation. Only call one agent at a time.
Process:
 1. Have profile_analyzer research the target user.
 2. Have message_writer create a personalized DM based on analysis.
 3. Have verifier check the message quality.
 4. If verification fails, coordinate improvements.
Finish when you have a crafted, verified DM. Return that DM only.
"""


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
        print(f"Update from subgraph {graph_id}:\n")
        is_subgraph = True

    for node_name, node_update in update.items():
        update_label = f"Update from node {node_name}:"
        if is_subgraph:
            update_label = "\t" + update_label
        print(update_label + "\n")

        # Handle structured response nodes
        if node_name == "generate_structured_response":
            print(f"Structured Response: {node_update}\n")
            continue

        # Handle regular message nodes
        if "messages" in node_update:
            messages = convert_to_messages(node_update["messages"])
            if last_message:
                messages = messages[-1:]
            for m in messages:
                pretty_print_message(m, indent=is_subgraph)
        else:
            print(f"Other update: {node_update}\n")


async def create_dm_supervisor():
    tools = await setup_instagram_tools()
    profile_analyzer, message_writer, verifier = await create_dm_agents(tools)

    dm_supervisor = create_supervisor(
        agents=[profile_analyzer, message_writer, verifier],
        model=ChatOpenAI(model=MODEL),
        prompt=supervisor_prompt + "\n\nAt the end, simply return the final DM and nothing else.",
        add_handoff_back_messages=True,
        output_mode="last_message",
    ).compile()

    return dm_supervisor


async def test_dm_supervisor():
    supervisor = await create_dm_supervisor()

    initial_state = {
        "messages": [{
            "role": "user",
            "content": "Research @andyx_p and create a personalized sales DM about our Anime Figurine. MAKE SURE TO CUSTOMISE IT TO THEIR PROFILE, EVEN IF THEY ONLY HAVE 1 POST."
        }]
    }

    print("\nStarting DM supervisor workflow...\n")

    async for chunk in supervisor.astream(initial_state, stream_mode="updates", subgraphs=True):
        pretty_print_messages(chunk)

    print("\nDM Creation Complete!\n")


if __name__ == "__main__":
    asyncio.run(test_dm_supervisor())
