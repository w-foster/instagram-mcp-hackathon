import asyncio
from app.services.instagram_client import InstagramClient
from app.utils.riddles import handle_riddle_conversation

CHECK_INTERVAL_SECONDS = 10 * 60  # 10 minutes

async def check_and_process_pending_chats(insta: InstagramClient):
    print("🔍 Checking for pending chats...")
    pending_resp = await insta.list_pending_chats(amount=20)
    
    if not pending_resp.get("threads"):
        print("⚠️ No pending chats found or error occurred.")
        return

    for thread in pending_resp["threads"]:
        thread_id = thread.get("thread_id") or thread.get("id")
        username = thread.get("username") or (thread.get("users") or [{}])[0].get("username")
        if not thread_id or not username:
            continue
        
        print(f"📥 Found pending chat from @{username} in thread {thread_id}")

        messages_resp = await insta.list_messages(thread_id=thread_id, amount=30)
        if not messages_resp.get("success"):
            print(f"❌ Failed to fetch messages for thread {thread_id}")
            continue

        messages = messages_resp.get("messages", [])
        if not messages:
            continue

        # Pass messages + username to your riddles handler
        await handle_riddle_conversation(insta, username, messages)

async def run_periodic_check():
    insta = InstagramClient()
    while True:
        try:
            await check_and_process_pending_chats(insta)
        except Exception as e:
            print(f"❌ Error during pending chat check: {e}")
        print(f"⏳ Sleeping {CHECK_INTERVAL_SECONDS // 60} minutes...\n")
        await asyncio.sleep(CHECK_INTERVAL_SECONDS)

if __name__ == "__main__":
    asyncio.run(run_periodic_check())
