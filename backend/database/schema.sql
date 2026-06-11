-- =====================================================
-- CONTACTS
-- =====================================================

CREATE TABLE contacts (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    company VARCHAR(255),
    status VARCHAR(50) DEFAULT 'Active',
    account_value NUMERIC(12,2) DEFAULT 0,
    churn_risk_score NUMERIC(5,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_contact_at TIMESTAMP
);


-- =====================================================
-- THREADS
-- =====================================================

CREATE TABLE threads (
    id SERIAL PRIMARY KEY,
    thread_id VARCHAR(255) UNIQUE NOT NULL,
    subject TEXT,
    sender_email VARCHAR(255),
    first_seen_at TIMESTAMP,
    last_updated_at TIMESTAMP,
    status VARCHAR(50) DEFAULT 'Open',
    assigned_to VARCHAR(255)
);


-- =====================================================
-- EMAILS
-- =====================================================

CREATE TABLE emails (
    id SERIAL PRIMARY KEY,
    thread_id INTEGER REFERENCES threads(id),

    message_id VARCHAR(255) UNIQUE NOT NULL,

    sender VARCHAR(255),

    subject TEXT,

    body TEXT,

    email_timestamp TIMESTAMP,

    category VARCHAR(100),

    sentiment VARCHAR(50),

    sentiment_score NUMERIC(4,3),

    urgency VARCHAR(50),

    requires_human BOOLEAN DEFAULT FALSE,

    confidence NUMERIC(4,3),

    raw_entities JSONB,

    status VARCHAR(50) DEFAULT 'Received',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- =====================================================
-- ACTIONS
-- =====================================================

CREATE TABLE actions (
    id SERIAL PRIMARY KEY,

    email_id INTEGER REFERENCES emails(id),

    action_type VARCHAR(100),

    agent_reasoning_log JSONB,

    proposed_content TEXT,

    is_approved BOOLEAN DEFAULT FALSE,

    approved_by VARCHAR(255),

    executed_at TIMESTAMP,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- =====================================================
-- KNOWLEDGE CHUNKS
-- =====================================================

CREATE TABLE knowledge_chunks (

    id SERIAL PRIMARY KEY,

    source_doc VARCHAR(255),

    chunk_index INTEGER,

    chunk_text TEXT NOT NULL,

    embedding JSONB,

    metadata JSONB,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- =====================================================
-- WEB CACHE
-- =====================================================

CREATE TABLE web_intelligence_cache (

    id SERIAL PRIMARY KEY,

    source_url TEXT,

    target_entity VARCHAR(255),

    scraped_data JSONB,

    scraped_at TIMESTAMP,

    expires_at TIMESTAMP
);


-- =====================================================
-- AUDIT LOG
-- =====================================================

CREATE TABLE audit_log (

    id SERIAL PRIMARY KEY,

    entity_type VARCHAR(100),

    entity_id INTEGER,

    action VARCHAR(100),

    performed_by VARCHAR(255),

    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    diff JSONB
);


-- =====================================================
-- TICKETS
-- =====================================================

CREATE TABLE tickets (

    id SERIAL PRIMARY KEY,

    email_id INTEGER REFERENCES emails(id),

    title VARCHAR(255),

    description TEXT,

    priority VARCHAR(50),

    assignee VARCHAR(255),

    status VARCHAR(50) DEFAULT 'Open',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- =====================================================
-- SENTIMENT HISTORY
-- =====================================================

CREATE TABLE sentiment_history (

    id SERIAL PRIMARY KEY,

    sender_email VARCHAR(255),

    email_id INTEGER REFERENCES emails(id),

    sentiment_score NUMERIC(4,3),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- =====================================================
-- ACCOUNT PROFILE
-- =====================================================

CREATE TABLE account_profiles (

    id SERIAL PRIMARY KEY,

    email VARCHAR(255) UNIQUE,

    subscription_tier VARCHAR(100),

    billing_status VARCHAR(100),

    renewal_date DATE,

    open_tickets INTEGER DEFAULT 0,

    account_value NUMERIC(12,2),

    notes TEXT
);