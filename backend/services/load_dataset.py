import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database.db import SessionLocal
from database.models import Contact
from database.models import Thread
from database.models import Email


# =====================================================
# CONFIG
# =====================================================

DATASET_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "email-data-advanced.json"


# =====================================================
# DATABASE SESSION
# =====================================================

db = SessionLocal()


# =====================================================
# LOAD DATASET
# =====================================================

with open(DATASET_PATH, "r", encoding="utf-8") as f:
    emails = json.load(f)

print(f"Loaded {len(emails)} emails")


# =====================================================
# CONTACT CREATION
# =====================================================

def create_contact(sender_email):

    existing_contact = (
        db.query(Contact)
        .filter(Contact.email == sender_email)
        .first()
    )

    if existing_contact:
        return existing_contact

    contact = Contact(
        email=sender_email
    )

    db.add(contact)
    db.commit()
    db.refresh(contact)

    return contact


# =====================================================
# THREAD CREATION
# =====================================================

def create_thread(email_data):

    thread_identifier = email_data["thread_id"]

    existing_thread = (
        db.query(Thread)
        .filter(Thread.thread_id == thread_identifier)
        .first()
    )

    if existing_thread:
        return existing_thread

    thread = Thread(
        thread_id=thread_identifier,
        subject=email_data.get("subject"),
        sender_email=email_data.get("sender"),
        status="Open"
    )

    db.add(thread)
    db.commit()
    db.refresh(thread)

    return thread


# =====================================================
# EMAIL CREATION
# =====================================================

def create_email(email_data, thread):

    existing_email = (
        db.query(Email)
        .filter(
            Email.message_id ==
            email_data["message_id"]
        )
        .first()
    )

    if existing_email:
        print(
            f"Skipping duplicate: "
            f"{email_data['message_id']}"
        )
        return

    email = Email(

        thread_id=thread.id,

        message_id=email_data["message_id"],

        sender=email_data.get("sender"),

        subject=email_data.get("subject"),

        body=email_data.get("body"),

        status="Received"

    )

    db.add(email)

    db.commit()

    print(
        f"Inserted: "
        f"{email_data['message_id']}"
    )


# =====================================================
# MAIN LOAD PROCESS
# =====================================================

def load_dataset():

    inserted = 0

    for email_data in emails:

        sender_email = email_data.get("sender")

        create_contact(sender_email)

        thread = create_thread(email_data)

        create_email(
            email_data,
            thread
        )

        inserted += 1

    print()

    print("=" * 50)

    print("DATA LOAD COMPLETE")

    print("=" * 50)

    print(
        f"Processed Emails: {inserted}"
    )


# =====================================================
# RUN
# =====================================================

if __name__ == "__main__":

    load_dataset()

    db.close()