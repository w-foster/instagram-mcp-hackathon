import os
from instagrapi import Client

SESSION_FILE_TEMPLATE = "session_{username}.json"


def init_client(username: str, password: str = None) -> Client:
    """
    Initialize an Instagrapi Client. If a session file exists for the username, load it;
    otherwise log in with password and save session.
    """
    cl = Client()
    session_file = SESSION_FILE_TEMPLATE.format(username=username)
    if os.path.exists(session_file):
        cl.load_settings(session_file)
        print(f"✅ Re-used session from {session_file}")
    else:
        if password is None:
            raise ValueError("Password required for first-time login.")
        cl.login(username, password)
        cl.dump_settings(session_file)
        print(f"💾 Logged in and saved session to {session_file}")
    return cl


def fetch_hashtag_usernames(
    hashtags: list[str],
    max_posts: int,
    username: str,
    password: str = None
) -> set[str]:
    """
    Fetch unique Instagram usernames that have posted the given hashtags.

    Parameters:
    - hashtags: list of hashtag strings without '#'.
    - max_posts: max number of posts to fetch per hashtag.
    - username: Instagram username for session.
    - password: Instagram password (needed only on first run).

    Returns:
    - A set of unique usernames.
    """
    cl = init_client(username, password)
    all_users: set[str] = set()
    for tag in hashtags:
        medias = cl.hashtag_medias_recent(tag, amount=max_posts)
        users = {m.user.username for m in medias}
        all_users |= users
    return all_users


# Example usage:
if __name__ == "__main__":
    hashtags = ["cats", "dogs"]
    max_posts = 10
    username = "instamcp4"
    password = "Password1."  # Only needed first time
    users = fetch_hashtag_usernames(hashtags, max_posts, username, password)
    print("Fetched users:")
    for u in sorted(users):
        print(u)
