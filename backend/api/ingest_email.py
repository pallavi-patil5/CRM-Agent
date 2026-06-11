from fastapi import APIRouter
from fastapi import HTTPException

from database.db import SessionLocal
from database.models import Thread
from database.models import Email
from database.models import Contact

from schemas.email_schema import EmailIngestRequest


router = APIRouter(
    prefix="/ingest",
    tags=["Email Ingestion"]
)


@router.post("/")
def ingest_email(
    email: EmailIngestRequest
):

    db = SessionLocal()

    try:

        # ===================================
        # DUPLICATE CHECK
        # ===================================

        existing_email = (
            db.query(Email)
            .filter(
                Email.message_id ==
                email.message_id
            )
            .first()
        )

        if existing_email:

            raise HTTPException(
                status_code=400,
                detail="Duplicate message_id"
            )

        # ===================================
        # CONTACT
        # ===================================

        contact = (
            db.query(Contact)
            .filter(
                Contact.email ==
                email.sender
            )
            .first()
        )

        if not contact:

            contact = Contact(
                email=email.sender
            )

            db.add(contact)

            db.commit()

        # ===================================
        # THREAD
        # ===================================

        thread = (
            db.query(Thread)
            .filter(
                Thread.thread_id ==
                email.thread_id
            )
            .first()
        )

        if not thread:

            thread = Thread(

                thread_id=email.thread_id,

                subject=email.subject,

                sender_email=email.sender,

                status="Open"
            )

            db.add(thread)

            db.commit()

            db.refresh(thread)

        # ===================================
        # EMAIL
        # ===================================

        new_email = Email(

            thread_id=thread.id,

            message_id=email.message_id,

            sender=email.sender,

            subject=email.subject,

            body=email.body,

            status="Received"
        )

        db.add(new_email)

        db.commit()

        db.refresh(new_email)

        return {

            "success": True,

            "email_id": new_email.id,

            "thread_id": thread.thread_id,

            "message": "Email ingested"
        }

    finally:

        db.close()