from database.db import SessionLocal
from database.models import Email

from services.gmail_reader import get_unread_emails


def ingest_gmail_emails():

    db = SessionLocal()

    emails = get_unread_emails()

    for email in emails:

        exists = db.query(Email).filter(
            Email.gmail_id == email["gmail_id"]
        ).first()

        if exists:
            continue

        new_email = Email(
            gmail_id=email["gmail_id"],
            thread_id=email["thread_id"],
            sender=email["sender"],
            subject=email["subject"],
            body=email["body"]
        )

        db.add(new_email)

    db.commit()

    db.close()