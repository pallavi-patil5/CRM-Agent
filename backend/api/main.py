from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware

from database.db import SessionLocal

from database.models import Email
from database.models import Ticket
from database.models import Action

from services.thread_service import ThreadService
from services.ticket_service import TicketService
from services.action_service import ActionService

from agent.triage_agent import TriageAgent

from api.ingest_email import router as ingest_router
from api.dashboard import router as dashboard_router
from api.analytics import router as analytics_router
from api.rag_api import router as rag_router
from api.gmail_api import router as gmail_router

app = FastAPI(
    title="Agentic Email CRM",
    version="1.0",
    description="Production-grade AI-powered CRM with autonomous triage agent"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest_router)
app.include_router(dashboard_router)
app.include_router(analytics_router)
app.include_router(rag_router)
app.include_router(gmail_router)

agent = TriageAgent()


# ==========================================
# DATABASE DEPENDENCY
# ==========================================

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# ==========================================
# HEALTH CHECK
# ==========================================

@app.get("/")
def root():

    return {
        "message":
            "Agentic Email CRM Running"
    }


# ==========================================
# PROCESS EMAIL
# ==========================================

@app.post("/process-email/{email_id}")
def process_email(
    email_id: int
):

    db = SessionLocal()

    email = (
        db.query(Email)
        .filter(
            Email.id == email_id
        )
        .first()
    )

    if not email:
        db.close()
        raise HTTPException(
            status_code=404,
            detail="Email not found"
        )

    result = agent.process_email(
        {
            "thread_id": email.thread.thread_id,
            "subject": email.subject,
            "body": email.body
        }
    )

    classification = result["classification"]

    # Save classification back to email
    email.category = classification.get("category")
    email.sentiment = classification.get("sentiment")
    email.urgency = classification.get("urgency")
    email.confidence = classification.get("confidence")
    email.requires_human = classification.get("requires_human", False)
    db.commit()

    # Save ticket if applicable
    ticket_service = TicketService()
    action_service = ActionService()

    if classification.get("category") in [
        "Complaint", "Refund", "Bug Report",
        "Security", "Legal", "Compliance"
    ]:
        ticket_service.create_from_classification(
            email_id=email.id,
            classification=classification
        )

    # Save action
    action_service.create_action(
        email_id=email.id,
        action_type=classification.get("category"),
        reasoning_trace=result["reasoning_trace"],
        proposed_content=result["draft_reply"]
    )

    ticket_service.close()
    action_service.close()
    db.close()

    return result


# ==========================================
# BULK PROCESS ALL EMAILS
# ==========================================

@app.post("/process-all-emails")
def process_all_emails():

    db = SessionLocal()
    emails = db.query(Email).all()
    processed = 0
    errors = []

    for email in emails:
        try:
            result = agent.process_email(
                {
                    "thread_id": email.thread.thread_id,
                    "subject": email.subject,
                    "body": email.body
                }
            )

            classification = result["classification"]
            email.category = classification.get("category")
            email.sentiment = classification.get("sentiment")
            email.urgency = classification.get("urgency")
            email.confidence = classification.get("confidence")
            email.requires_human = classification.get("requires_human", False)
            db.commit()

            ticket_service = TicketService()
            action_service = ActionService()

            if classification.get("category") in [
                "Complaint", "Refund", "Bug Report",
                "Security", "Legal", "Compliance"
            ]:
                ticket_service.create_from_classification(
                    email_id=email.id,
                    classification=classification
                )

            action_service.create_action(
                email_id=email.id,
                action_type=classification.get("category"),
                reasoning_trace=result["reasoning_trace"],
                proposed_content=result["draft_reply"]
            )

            ticket_service.close()
            action_service.close()
            processed += 1

        except Exception as e:
            errors.append({"email_id": email.id, "error": str(e)})

    db.close()

    return {
        "processed": processed,
        "total": len(emails),
        "errors": errors
    }


# ==========================================
# DRY RUN — Agent planning mode, no execution
# ==========================================

@app.post("/agent/dry-run/{email_id}")
def agent_dry_run(email_id: int):

    db = SessionLocal()
    email = db.query(Email).filter(Email.id == email_id).first()

    if not email:
        db.close()
        raise HTTPException(status_code=404, detail="Email not found")

    result = agent.process_email(
        {
            "thread_id": email.thread.thread_id,
            "subject": email.subject,
            "body": email.body
        },
        dry_run=True
    )

    db.close()
    return result


# ==========================================
# GET THREAD
# ==========================================

@app.get("/thread/{thread_id}")
def get_thread(
    thread_id: str
):

    service = ThreadService()

    history = (
        service.build_thread_history(
            thread_id
        )
    )

    summary = (
        service.get_thread_summary(
            thread_id
        )
    )

    service.close()

    return {

        "summary":
            summary,

        "history":
            history
    }


# ==========================================
# GET ALL TICKETS
# ==========================================

@app.get("/tickets")
def get_tickets():

    db = SessionLocal()

    tickets = db.query(
        Ticket
    ).all()

    result = []

    for ticket in tickets:

        result.append(
            {
                "id":
                    ticket.id,

                "title":
                    ticket.title,

                "priority":
                    ticket.priority,

                "status":
                    ticket.status,

                "assignee":
                    ticket.assignee
            }
        )

    db.close()

    return result


# ==========================================
# GET ALL ACTIONS
# ==========================================

@app.get("/actions")
def get_actions():

    db = SessionLocal()

    actions = db.query(
        Action
    ).all()

    result = []

    for action in actions:

        result.append(
            {
                "id":
                    action.id,

                "type":
                    action.action_type,

                "approved":
                    action.is_approved,

                "approved_by":
                    action.approved_by
            }
        )

    db.close()

    return result


# ==========================================
# GET EMAIL
# ==========================================

@app.get("/email/{email_id}")
def get_email(
    email_id: int
):

    db = SessionLocal()

    email = (
        db.query(Email)
        .filter(
            Email.id == email_id
        )
        .first()
    )

    if not email:

        raise HTTPException(
            status_code=404,
            detail="Email not found"
        )

    response = {

        "id":
            email.id,

        "message_id":
            email.message_id,

        "sender":
            email.sender,

        "subject":
            email.subject,

        "body":
            email.body,

        "category":
            email.category,

        "urgency":
            email.urgency
    }

    db.close()

    return response