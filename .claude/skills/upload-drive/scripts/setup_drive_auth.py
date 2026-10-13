#!/usr/bin/env python3
"""
Setup Google Drive OAuth2 authentication.
Creates/refreshes token.json for Drive API access.

Usage:
    python3 setup_drive_auth.py
    python3 setup_drive_auth.py --credentials-path /path/to/credentials.json
"""

import argparse
import os
import sys


def find_env_file():
    """Walk up directories to find .env file."""
    d = os.path.dirname(os.path.abspath(__file__))
    for _ in range(10):
        env_path = os.path.join(d, ".env")
        if os.path.exists(env_path):
            return env_path
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    return None


def load_env():
    """Load .env file into os.environ."""
    env_path = find_env_file()
    if env_path:
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    os.environ.setdefault(key.strip(), value.strip())


def main():
    parser = argparse.ArgumentParser(description="Setup Google Drive OAuth2 auth")
    parser.add_argument(
        "--credentials-path", help="Path to credentials.json (overrides .env)"
    )
    args = parser.parse_args()

    load_env()

    creds_path = args.credentials_path or os.environ.get("GOOGLE_CREDENTIALS_PATH")
    if not creds_path:
        print(
            "ERROR: GOOGLE_CREDENTIALS_PATH not set in .env and --credentials-path not provided."
        )
        print("  1. Go to https://console.cloud.google.com/apis/credentials")
        print("  2. Create OAuth 2.0 Client ID (Desktop app)")
        print("  3. Download credentials.json")
        print("  4. Set GOOGLE_CREDENTIALS_PATH in .env")
        sys.exit(1)

    creds_path = os.path.expanduser(creds_path)
    if not os.path.exists(creds_path):
        print(f"ERROR: Credentials file not found: {creds_path}")
        sys.exit(1)

    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError:
        print("ERROR: Required packages not installed. Run:")
        print(
            "  pip install google-auth google-auth-oauthlib google-api-python-client"
        )
        sys.exit(1)

    SCOPES = ["https://www.googleapis.com/auth/drive"]
    token_path = os.path.join(os.path.dirname(creds_path), "token.json")

    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if creds and creds.valid:
        print(f"Token valid: {token_path}")
        print("Authentication OK — no action needed.")
        return

    if creds and creds.expired and creds.refresh_token:
        print("Token expired, refreshing...")
        try:
            creds.refresh(Request())
            with open(token_path, "w") as f:
                f.write(creds.to_json())
            print(f"Token refreshed: {token_path}")
            return
        except Exception as e:
            print(f"Refresh failed ({e}), starting new OAuth flow...")

    print("Starting OAuth2 flow — a browser window will open...")
    flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
    creds = flow.run_local_server(port=0)

    with open(token_path, "w") as f:
        f.write(creds.to_json())
    print(f"Token saved: {token_path}")
    print("Authentication complete!")


if __name__ == "__main__":
    main()
