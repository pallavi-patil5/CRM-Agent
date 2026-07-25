import os
import base64
import email as email_lib
from pathlib import Path

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

BASE_DIR = Path(__file__).resolve().parent.parent
CREDENTIALS_FILE = BASE_DIR / os.getenv("GMAIL_CREDENTIALS_FILE", "credentials.json")
TOKEN_FILE = BASE_DIR / os.getenv("GMAIL_TOKEN_FILE", "token.json")


def get_gmail_service():
    creds = None

    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def decode_body(payload):
    """Recursively extract plain text body from Gmail message payload."""
    if payload.get("mimeType") == "text/plain":
        data = payload.get("body", {}).get("data", "")
        return base64.urlsafe_b64decode(data + "==").decode("utf-8", errors="replace") if data else ""

    if payload.get("mimeType", "").startswith("multipart"):
        for part in payload.get("parts", []):
            text = decode_body(part)
            if text:
                return text

    return ""


def fetch_unread_emails(max_results: int = 50, label: str = "INBOX") -> list[dict]:
    """Fetch unread emails from Gmail and return normalized dicts."""
    service = get_gmail_service()

    response = service.users().messages().list(
        userId="me",
        labelIds=[label, "UNREAD"],
        maxResults=max_results
    ).execute()

    messages = response.get("messages", [])
    results = []

    for msg_ref in messages:
        msg = service.users().messages().get(
            userId="me", id=msg_ref["id"], format="full"
        ).execute()

        headers = {h["name"].lower(): h["value"] for h in msg["payload"].get("headers", [])}

        sender = headers.get("from", "unknown@unknown.com")
        subject = headers.get("subject", "(no subject)")
        date = headers.get("date", "")
        gmail_thread_id = msg.get("threadId", msg["id"])
        message_id = headers.get("message-id") or msg["id"]
        body = decode_body(msg["payload"])

        results.append({
            "message_id": message_id,
            "gmail_id": msg["id"],
            "thread_id": f"gmail_{gmail_thread_id}",
            "sender": sender,
            "subject": subject,
            "body": body,
            "timestamp": date,
        })

    return results


def mark_as_read(gmail_id: str):
    """Remove UNREAD label from a Gmail message."""
    service = get_gmail_service()
    service.users().messages().modify(
        userId="me",
        id=gmail_id,
        body={"removeLabelIds": ["UNREAD"]}
    ).execute()
