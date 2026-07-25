from services.gmail_service import get_gmail_service

def mark_as_read(message_id):

    service = get_gmail_service()

    service.users().messages().modify(
        userId="me",
        id=message_id,
        body={
            "removeLabelIds": ["UNREAD"]
        }
    ).execute()

from email.mime.text import MIMEText
import base64

def send_reply(reply_text):

    service = get_gmail_service()

    message = MIMEText(reply_text)

    raw = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode()

    service.users().messages().send(
        userId="me",
        body={
            "raw": raw
        }
    ).execute()