import asyncio
from app.services.instagram_client import InstagramClient
from app.utils.riddles import handle_riddle_conversation

CHECK_INTERVAL_SECONDS = 10 * 60  # 10 minutes

async def check_and_process_unread_chats(insta: InstagramClient):
    print("🔍 Checking for unread chats...")
    chats_resp = await insta.list_chats(amount=20)
    
    if not chats_resp.get("success") or not chats_resp.get("threads"):
        print("⚠️ No chats found or error occurred.")
        return

    for thread in chats_resp["threads"]:
        thread_id = thread.get("thread_id")
        users = thread.get("users", [])
        username = None
        if users:
            username = users[0].get("username")

        if not thread_id or not username:
            continue

        last_message = thread.get("last_message") or {}
        last_sender = last_message.get("user", {}).get("username") or last_message.get("username")

        my_username = "instamcp2"  # insta name

        if last_sender and last_sender.lower() == my_username.lower():
            # We sent the last message, skip
            continue

        print(f"📥 Unread chat from @{username} in thread {thread_id}, last sender: {last_sender}")

        messages_resp = await insta.list_messages(thread_id=thread_id, amount=10)
        if not messages_resp.get("success"):
            print(f"❌ Failed to fetch messages for thread {thread_id}")
            continue

        messages = messages_resp.get("messages", [])
        if not messages:
            continue

        await handle_riddle_conversation(insta, username, messages)

async def run_periodic_check():
    insta = InstagramClient()
    while True:
        try:
            await check_and_process_unread_chats(insta)
        except Exception as e:
            print(f"❌ Error during unread chat check: {e}")
        print(f"⏳ Sleeping {CHECK_INTERVAL_SECONDS // 60} minutes...\n")
        await asyncio.sleep(CHECK_INTERVAL_SECONDS)

if __name__ == "__main__":
    asyncio.run(run_periodic_check())
