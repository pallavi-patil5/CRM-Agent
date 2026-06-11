from fastapi import APIRouter
from sqlalchemy import func

from database.db import SessionLocal
from database.models import Email
from database.models import Ticket


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


# ==========================================
# SUMMARY
# ==========================================

@router.get("/summary")
def get_summary():

    db = SessionLocal()

    total_emails = db.query(Email).count()
    total_tickets = db.query(Ticket).count()
    open_tickets = db.query(Ticket).filter(Ticket.status == "Open").count()
    closed_tickets = db.query(Ticket).filter(Ticket.status == "Closed").count()

    db.close()

    return {
        "total_emails": total_emails,
        "total_tickets": total_tickets,
        "open_tickets": open_tickets,
        "closed_tickets": closed_tickets
    }


# ==========================================
# ALL EMAILS (for inbox)
# ==========================================

@router.get("/emails")
def get_all_emails():

    db = SessionLocal()
    emails = db.query(Email).order_by(Email.id.desc()).limit(200).all()
    db.close()

    return [
        {
            "id": e.id,
            "message_id": e.message_id,
            "sender": e.sender,
            "subject": e.subject,
            "body": e.body,
            "category": e.category,
            "sentiment": e.sentiment,
            "sentiment_score": float(e.sentiment_score) if e.sentiment_score else None,
            "urgency": e.urgency,
            "requires_human": e.requires_human,
            "confidence": float(e.confidence) if e.confidence else None,
            "status": e.status
        }
        for e in emails
    ]


# ==========================================
# CATEGORY DISTRIBUTION
# ==========================================

@router.get("/categories")
def category_distribution():

    db = SessionLocal()

    results = (

        db.query(
            Email.category,
            func.count(Email.id)
        )

        .group_by(
            Email.category
        )

        .all()
    )

    db.close()

    return [

        {
            "category": row[0],
            "count": row[1]
        }

        for row in results
    ]


# ==========================================
# SENTIMENT DISTRIBUTION
# ==========================================

@router.get("/sentiment")
def sentiment_distribution():

    db = SessionLocal()

    results = (

        db.query(
            Email.sentiment,
            func.count(Email.id)
        )

        .group_by(
            Email.sentiment
        )

        .all()
    )

    db.close()

    return [

        {
            "sentiment": row[0],
            "count": row[1]
        }

        for row in results
    ]


# ==========================================
# TICKET PRIORITIES
# ==========================================

@router.get("/tickets")
def ticket_priorities():

    db = SessionLocal()

    results = (

        db.query(
            Ticket.priority,
            func.count(Ticket.id)
        )

        .group_by(
            Ticket.priority
        )

        .all()
    )

    db.close()

    return [

        {
            "priority": row[0],
            "count": row[1]
        }

        for row in results
    ]