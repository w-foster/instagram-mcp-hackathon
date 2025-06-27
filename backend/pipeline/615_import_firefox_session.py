#!/usr/bin/env python3
from argparse import ArgumentParser
from glob import glob
from os.path import expanduser
from platform import system
from sqlite3 import OperationalError, connect

from instaloader import Instaloader

def get_cookiefile():
    default = {
        "Windows": "~/AppData/Roaming/Mozilla/Firefox/Profiles/*/cookies.sqlite",
        "Darwin": "~/Library/Application Support/Firefox/Profiles/*/cookies.sqlite",
    }.get(system(), "~/.mozilla/firefox/*/cookies.sqlite")
    files = glob(expanduser(default))
    if not files:
        raise SystemExit("No Firefox cookies.sqlite found; use -c COOKIEFILE.")
    return files[0]

def import_session(cookiefile, sessionfile, username):
    print(f"Using cookies from {cookiefile}")
    conn = connect(f"file:{cookiefile}?immutable=1", uri=True)
    try:
        rows = conn.execute(
            "SELECT name, value FROM moz_cookies WHERE baseDomain='instagram.com'"
        )
    except OperationalError:
        rows = conn.execute(
            "SELECT name, value FROM moz_cookies WHERE host LIKE '%instagram.com'"
        )

    L = Instaloader(max_connection_attempts=1)
    # Load cookies into Instaloader’s session
    for name, value in rows:
        L.context._session.cookies.set(name, value, domain=".instagram.com")
    # Bypass test_login entirely
    L.context.username = username
    L.save_session_to_file(sessionfile)
    print(f"✅ Saved session for '{username}' to {sessionfile}")

if __name__ == "__main__":
    p = ArgumentParser(description="Import Instagram session from Firefox cookies")
    p.add_argument("-c", "--cookiefile", help="Path to Firefox cookies.sqlite")
    p.add_argument("-f", "--sessionfile", required=True,
                   help="Path to write Instaloader session file")
    p.add_argument("-u", "--login-user", required=True,
                   help="Instagram username (for the session file)")
    args = p.parse_args()
    cookiefile = args.cookiefile or get_cookiefile()
    import_session(cookiefile, args.sessionfile, args.login_user)
