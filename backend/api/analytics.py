import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import APIRouter, Query
from sqlalchemy import func
from datetime import datetime, timedelta

from database.db import SessionLocal
from database.models import Email, Contact, Thread, Ticket, SentimentHistory


router = APIRouter(tags=["Analytics"])


# ==========================================
# SENTIMENT TREND
# ==========================================

@router.get("/analytics/sentiment-trend")
def sentiment_trend(
    sender: str = Query(None, description="Filter by sender email"),
    days: int = Query(30, description="Number of days to look back")
):
    db = SessionLocal()
    cutoff = datetime.utcnow() - timedelta(days=days)

    query = db.query(
        Email.sender,
        Email.created_at,
        Email.sentiment,
        Email.sentiment_score
    ).filter(
        Email.created_at >= cutoff,
        Email.sentiment_score != None
    )

    if sender:
        query = query.filter(Email.sender == sender)

    results = query.order_by(Email.created_at.asc()).all()
    db.close()

    data = [
        {
            "sender": r.sender,
            "timestamp": r.created_at.isoformat() if r.created_at else None,
            "sentiment": r.sentiment,
            "sentiment_score": float(r.sentiment_score) if r.sentiment_score else None
        }
        for r in results
    ]

    # Compute moving average per sender
    sender_map = {}
    for item in data:
        s = item["sender"]
        if s not in sender_map:
            sender_map[s] = []
        sender_map[s].append(item)

    # Detect deterioration: 3+ consecutive negatives
    alerts = []
    for s, emails in sender_map.items():
        consecutive_negative = 0
        for e in emails:
            score = e.get("sentiment_score") or 0
            if score < -0.3:
                consecutive_negative += 1
            else:
                consecutive_negative = 0
            if consecutive_negative >= 3:
                alerts.append({
                    "sender": s,
                    "alert": "3+ consecutive negative emails — escalation recommended"
                })
                break

    return {
        "trend_data": data,
        "sender_summary": {
            s: {
                "email_count": len(emails),
                "avg_sentiment_score": round(
                    sum(e["sentiment_score"] or 0 for e in emails) / len(emails), 3
                )
            }
            for s, emails in sender_map.items()
        },
        "deterioration_alerts": alerts
    }


# ==========================================
# CATEGORY BREAKDOWN
# ==========================================

@router.get("/analytics/category-breakdown")
def category_breakdown(
    days: int = Query(30, description="Number of days to look back")
):
    db = SessionLocal()
    cutoff = datetime.utcnow() - timedelta(days=days)

    results = (
        db.query(Email.category, func.count(Email.id))
        .filter(Email.created_at >= cutoff)
        .group_by(Email.category)
        .all()
    )
    db.close()

    return [{"category": r[0] or "Unclassified", "count": r[1]} for r in results]


# ==========================================
# CONTACTS
# ==========================================

@router.get("/contacts/{email}")
def get_contact(email: str):
    db = SessionLocal()

    contact = db.query(Contact).filter(Contact.email == email).first()
    if not contact:
        db.close()
        return {"error": "Contact not found", "email": email}

    threads = db.query(Thread).filter(Thread.sender_email == email).all()
    open_tickets = (
        db.query(Ticket)
        .join(Email, Ticket.email_id == Email.id)
        .filter(Email.sender == email, Ticket.status == "Open")
        .count()
    )

    emails = db.query(Email).filter(Email.sender == email).order_by(Email.created_at.desc()).all()
    sentiment_scores = [
        float(e.sentiment_score) for e in emails if e.sentiment_score is not None
    ]
    avg_sentiment = round(sum(sentiment_scores) / len(sentiment_scores), 3) if sentiment_scores else None

    db.close()

    return {
        "email": contact.email,
        "name": contact.name,
        "company": contact.company,
        "status": contact.status,
        "account_value": float(contact.account_value) if contact.account_value else 0,
        "churn_risk_score": float(contact.churn_risk_score) if contact.churn_risk_score else 0,
        "created_at": contact.created_at.isoformat() if contact.created_at else None,
        "last_contact_at": contact.last_contact_at.isoformat() if contact.last_contact_at else None,
        "open_tickets": open_tickets,
        "thread_count": len(threads),
        "avg_sentiment_score": avg_sentiment,
        "recent_emails": [
            {
                "subject": e.subject,
                "category": e.category,
                "sentiment": e.sentiment,
                "urgency": e.urgency,
                "created_at": e.created_at.isoformat() if e.created_at else None
            }
            for e in emails[:5]
        ]
    }


@router.patch("/contacts/{email}/status")
def update_contact_status(email: str, status: str):
    db = SessionLocal()
    contact = db.query(Contact).filter(Contact.email == email).first()
    if not contact:
        db.close()
        return {"error": "Contact not found"}
    contact.status = status
    db.commit()
    db.close()
    return {"success": True, "email": email, "new_status": status}


# ==========================================
# THREADS BY CONTACT
# ==========================================

@router.get("/threads/contact/{contact_email}")
def get_threads_by_contact(contact_email: str):
    db = SessionLocal()

    threads = (
        db.query(Thread)
        .filter(Thread.sender_email == contact_email)
        .all()
    )

    result = []
    for thread in threads:
        emails = (
            db.query(Email)
            .filter(Email.thread_id == thread.id)
            .order_by(Email.created_at.asc())
            .all()
        )
        result.append({
            "thread_id": thread.thread_id,
            "subject": thread.subject,
            "status": thread.status,
            "email_count": len(emails),
            "emails": [
                {
                    "id": e.id,
                    "message_id": e.message_id,
                    "subject": e.subject,
                    "category": e.category,
                    "sentiment": e.sentiment,
                    "urgency": e.urgency,
                    "created_at": e.created_at.isoformat() if e.created_at else None
                }
                for e in emails
            ]
        })

    db.close()
    return result
