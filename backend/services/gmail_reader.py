import base64

from services.gmail_service import get_gmail_service


def get_unread_emails():

    service = get_gmail_service()

    results = service.users().messages().list(
        userId="me",
        q="is:unread"
    ).execute()

    messages = results.get("messages", [])

    emails = []

    for msg in messages:

        message = service.users().messages().get(
            userId="me",
            id=msg["id"]
        ).execute()

        headers = message["payload"]["headers"]

        subject = ""
        sender = ""

        for h in headers:

            if h["name"] == "Subject":
                subject = h["value"]

            if h["name"] == "From":
                sender = h["value"]

        body = ""

        try:
            parts = message["payload"]["parts"]

            for part in parts:

                if part["mimeType"] == "text/plain":

                    data = part["body"]["data"]

                    body = base64.urlsafe_b64decode(
                        data
                    ).decode()

                    break

        except:
            pass

        emails.append({
            "gmail_id": msg["id"],
            "thread_id": message["threadId"],
            "sender": sender,
            "subject": subject,
            "body": body
        })

    return emails