from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    JSON,
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database.db import Base


# =====================================================
# CONTACTS
# =====================================================

class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)

    email = Column(String, unique=True, nullable=False)

    name = Column(String)

    company = Column(String)

    status = Column(String, default="Active")

    account_value = Column(Numeric(12, 2), default=0)

    churn_risk_score = Column(Numeric(5, 2), default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    last_contact_at = Column(DateTime(timezone=True))


# =====================================================
# THREADS
# =====================================================

class Thread(Base):
    __tablename__ = "threads"

    id = Column(Integer, primary_key=True)

    thread_id = Column(String, unique=True, nullable=False)

    subject = Column(Text)

    sender_email = Column(String)

    first_seen_at = Column(DateTime(timezone=True))

    last_updated_at = Column(DateTime(timezone=True))

    status = Column(String, default="Open")

    assigned_to = Column(String)

    emails = relationship(
        "Email",
        back_populates="thread",
        cascade="all, delete"
    )


# =====================================================
# EMAILS
# =====================================================

class Email(Base):
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True)

    thread_id = Column(
        Integer,
        ForeignKey("threads.id")
    )

    message_id = Column(
        String,
        unique=True,
        nullable=False
    )

    sender = Column(String)

    subject = Column(Text)

    body = Column(Text)

    email_timestamp = Column(DateTime(timezone=True))

    category = Column(String)

    sentiment = Column(String)

    sentiment_score = Column(Numeric(4, 3))

    urgency = Column(String)

    requires_human = Column(Boolean, default=False)

    confidence = Column(Numeric(4, 3))

    raw_entities = Column(JSON)

    status = Column(String, default="Received")

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    thread = relationship(
        "Thread",
        back_populates="emails"
    )


# =====================================================
# ACTIONS
# =====================================================

class Action(Base):
    __tablename__ = "actions"

    id = Column(Integer, primary_key=True)

    email_id = Column(
        Integer,
        ForeignKey("emails.id")
    )

    action_type = Column(String)

    agent_reasoning_log = Column(JSON)

    proposed_content = Column(Text)

    is_approved = Column(Boolean, default=False)

    approved_by = Column(String)

    executed_at = Column(DateTime(timezone=True))

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )


# =====================================================
# KNOWLEDGE CHUNKS
# =====================================================

class KnowledgeChunk(Base):
    __tablename__ = "knowledge_chunks"

    id = Column(Integer, primary_key=True)

    source_doc = Column(String)

    chunk_index = Column(Integer)

    chunk_text = Column(Text)

    embedding = Column(JSON)

    chunk_metadata = Column(JSON)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )


# =====================================================
# WEB CACHE
# =====================================================

class WebIntelligenceCache(Base):
    __tablename__ = "web_intelligence_cache"

    id = Column(Integer, primary_key=True)

    source_url = Column(Text)

    target_entity = Column(String)

    scraped_data = Column(JSON)

    scraped_at = Column(DateTime(timezone=True))

    expires_at = Column(DateTime(timezone=True))


# =====================================================
# AUDIT LOG
# =====================================================

class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True)

    entity_type = Column(String)

    entity_id = Column(Integer)

    action = Column(String)

    performed_by = Column(String)

    timestamp = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    diff = Column(JSON)


# =====================================================
# TICKETS
# =====================================================

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True)

    email_id = Column(
        Integer,
        ForeignKey("emails.id")
    )

    title = Column(String)

    description = Column(Text)

    priority = Column(String)

    assignee = Column(String)

    status = Column(String, default="Open")

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )


# =====================================================
# SENTIMENT HISTORY
# =====================================================

class SentimentHistory(Base):
    __tablename__ = "sentiment_history"

    id = Column(Integer, primary_key=True)

    sender_email = Column(String)

    email_id = Column(
        Integer,
        ForeignKey("emails.id")
    )

    sentiment_score = Column(Numeric(4, 3))

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )


# =====================================================
# ACCOUNT PROFILE
# =====================================================

class AccountProfile(Base):
    __tablename__ = "account_profiles"

    id = Column(Integer, primary_key=True)

    email = Column(
        String,
        unique=True
    )

    subscription_tier = Column(String)

    billing_status = Column(String)

    renewal_date = Column(Date)

    open_tickets = Column(Integer, default=0)

    account_value = Column(Numeric(12, 2))

    notes = Column(Text)