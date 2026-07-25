import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import APIRouter, HTTPException
from database.db import SessionLocal
from database.models import Email, Thread, Contact
from services.gmail_service import fetch_unread_emails, mark_as_read, TOKEN_FILE, CREDENTIALS_FILE

router = APIRouter(prefix="/gmail", tags=["Gmail"])


@router.get("/status")
def gmail_status():
    """Check if Gmail OAuth token exists and credentials file is present."""
    return {
        "credentials_file": CREDENTIALS_FILE.exists(),
        "token_file": TOKEN_FILE.exists(),
        "authenticated": TOKEN_FILE.exists(),
    }


@router.post("/sync")
def gmail_sync(max_results: int = 50, mark_read: bool = False):
    """
    Fetch unread Gmail emails and ingest new ones into the CRM.
    Skips duplicates by message_id.
    """
    try:
        emails = fetch_unread_emails(max_results=max_results)
    except FileNotFoundError:
        raise HTTPException(status_code=400, detail="credentials.json not found in backend/. Download it from Google Cloud Console.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gmail API error: {str(e)}")

    db = SessionLocal()
    ingested = 0
    skipped = 0

    try:
        for e in emails:
            # Dedup check
            if db.query(Email).filter(Email.message_id == e["message_id"]).first():
                skipped += 1
                continue

            # Upsert contact
            contact = db.query(Contact).filter(Contact.email == e["sender"]).first()
            if not contact:
                contact = Contact(email=e["sender"])
                db.add(contact)
                db.commit()

            # Upsert thread
            thread = db.query(Thread).filter(Thread.thread_id == e["thread_id"]).first()
            if not thread:
                thread = Thread(
                    thread_id=e["thread_id"],
                    subject=e["subject"],
                    sender_email=e["sender"],
                    status="Open"
                )
                db.add(thread)
                db.commit()
                db.refresh(thread)

            # Insert email
            new_email = Email(
                thread_id=thread.id,
                message_id=e["message_id"],
                sender=e["sender"],
                subject=e["subject"],
                body=e["body"],
                status="Received"
            )
            db.add(new_email)
            db.commit()
            ingested += 1

            if mark_read:
                try:
                    mark_as_read(e["gmail_id"])
                except Exception:
                    pass

    finally:
        db.close()

    return {
        "ingested": ingested,
        "skipped_duplicates": skipped,
        "total_fetched": len(emails),
    }
