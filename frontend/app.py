import requests
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import time

API_BASE = "http://localhost:8000"

st.set_page_config(
    page_title="Agentic Email CRM",
    layout="wide",
    page_icon="📧"
)

# =====================================
# HELPERS
# =====================================

SENTIMENT_COLOR = {
    "Positive": "🟢",
    "Neutral": "🟡",
    "Negative": "🔴",
    "Mixed": "🟠"
}

URGENCY_COLOR = {
    "Critical": "🔴",
    "High": "🟠",
    "Medium": "🟡",
    "Low": "🟢"
}

CATEGORY_BADGE = {
    "Security": "🔐",
    "Legal": "⚖️",
    "Compliance": "📋",
    "Refund": "💰",
    "Complaint": "😠",
    "Bug Report": "🐛",
    "Billing": "🧾",
    "Feature Request": "✨",
    "Spam": "🚫",
    "Internal": "🏢",
    "General Inquiry": "💬",
    "Sales": "📈"
}

def safe_get(url, default=None):
    try:
        r = requests.get(url, timeout=5)
        return r.json() if r.status_code == 200 else default
    except Exception:
        return default

def safe_post(url, json=None):
    try:
        r = requests.post(url, json=json, timeout=120)
        try:
            return r.status_code, r.json()
        except Exception:
            return r.status_code, {"error": r.text[:500] if r.text else "Empty response from server"}
    except Exception as e:
        return 500, {"error": str(e)}


# =====================================
# NAVIGATION
# =====================================

st.sidebar.title("📧 Agentic CRM")
page = st.sidebar.radio(
    "Navigation",
    ["🏠 Mission Control", "📬 Thread Workspace", "📊 Analytics", "🔍 RAG Debug", "⚙️ Bulk Operations"]
)

# =====================================
# PAGE 1 — MISSION CONTROL INBOX
# =====================================

if page == "🏠 Mission Control":

    st.title("📧 Mission Control — Email Inbox")

    summary = safe_get(f"{API_BASE}/dashboard/summary", {})

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Emails", summary.get("total_emails", 0))
    col2.metric("Total Tickets", summary.get("total_tickets", 0))
    col3.metric("Open Tickets", summary.get("open_tickets", 0))
    col4.metric("Closed Tickets", summary.get("closed_tickets", 0))

    st.divider()

    # Tabs
    tab_all, tab_human, tab_escalated, tab_spam = st.tabs([
        "All Emails", "Needs Human Review", "Escalated", "Spam"
    ])

    emails_raw = safe_get(f"{API_BASE}/dashboard/emails", [])

    def render_email_table(emails, filter_fn=None, tab_key=""):
        if filter_fn:
            emails = [e for e in emails if filter_fn(e)]
        if not emails:
            st.info("No emails in this category.")
            return
        for e in emails:
            cat = e.get("category") or "Unclassified"
            sentiment = e.get("sentiment") or "Neutral"
            urgency = e.get("urgency") or "—"
            badge = CATEGORY_BADGE.get(cat, "📧")
            sent_icon = SENTIMENT_COLOR.get(sentiment, "⚪")
            urg_icon = URGENCY_COLOR.get(urgency, "⚪")

            with st.expander(
                f"{urg_icon} [{e.get('id')}] {e.get('subject', 'No Subject')} — {sent_icon} {sentiment} | {badge} {cat}"
            ):
                col_a, col_b = st.columns([2, 1])
                with col_a:
                    st.write(f"**From:** {e.get('sender', '')}")
                    st.write(f"**Body:** {str(e.get('body', ''))[:300]}...")
                with col_b:
                    st.write(f"**Category:** {badge} {cat}")
                    st.write(f"**Urgency:** {urg_icon} {urgency}")
                    st.write(f"**Sentiment:** {sent_icon} {sentiment}")
                    st.write(f"**Confidence:** {e.get('confidence') or '—'}")
                    if st.button(f"🤖 Process Email #{e['id']}", key=f"proc_{tab_key}_{e['id']}"):
                        with st.spinner("Agent processing..."):
                            status, result = safe_post(f"{API_BASE}/process-email/{e['id']}")
                            if status == 200:
                                st.success("✅ Processed")
                                st.json(result.get("classification", {}))
                            else:
                                st.error(str(result))
                    if st.button(f"🔍 Dry Run #{e['id']}", key=f"dry_{tab_key}_{e['id']}"):
                        with st.spinner("Planning..."):
                            status, result = safe_post(f"{API_BASE}/agent/dry-run/{e['id']}")
                            if status == 200:
                                st.info("🔍 DRY RUN — No actions executed")
                                st.json(result)
                            else:
                                st.error(str(result))

    with tab_all:
        render_email_table(emails_raw, tab_key="all")
    with tab_human:
        render_email_table(emails_raw, lambda e: e.get("requires_human"), tab_key="human")
    with tab_escalated:
        render_email_table(emails_raw, lambda e: e.get("urgency") in ["Critical", "High"], tab_key="esc")
    with tab_spam:
        render_email_table(emails_raw, lambda e: e.get("category") == "Spam", tab_key="spam")

    # All Tickets
    st.divider()
    st.subheader("🎫 All Tickets")
    tickets = safe_get(f"{API_BASE}/tickets", [])
    if tickets:
        st.dataframe(pd.DataFrame(tickets), use_container_width=True)
    else:
        st.info("No tickets yet. Process emails to generate tickets.")


# =====================================
# PAGE 2 — THREAD WORKSPACE
# =====================================

elif page == "📬 Thread Workspace":

    st.title("📬 Thread Workspace")

    contact_email = st.text_input("Enter sender email to load thread", placeholder="e.g. bob.jones@enterprise.net")

    if contact_email:
        threads = safe_get(f"{API_BASE}/threads/contact/{contact_email}", [])
        contact = safe_get(f"{API_BASE}/contacts/{contact_email}", {})

        col_thread, col_contact = st.columns([2, 1])

        with col_contact:
            st.subheader("👤 Contact Profile")
            if contact and not contact.get("error"):
                status = contact.get("status") or "Active"
                account_val = contact.get("account_value", 0)
                churn_risk = contact.get("churn_risk_score", 0)
                avg_sent = contact.get("avg_sentiment_score")

                st.write(f"**Email:** {contact.get('email')}")
                st.write(f"**Name:** {contact.get('name') or '—'}")
                st.write(f"**Company:** {contact.get('company') or '—'}")
                st.write(f"**Status:** {status}")
                st.write(f"**Account Value:** ${account_val:,.2f}")
                st.write(f"**Churn Risk:** {churn_risk}")
                st.write(f"**Avg Sentiment:** {avg_sent}")
                st.write(f"**Open Tickets:** {contact.get('open_tickets', 0)}")
                st.write(f"**Thread Count:** {contact.get('thread_count', 0)}")
            else:
                st.info("Contact not found in CRM.")

        with col_thread:
            if not threads:
                st.info("No threads found for this email.")
            for thread in threads:
                st.subheader(f"🧵 Thread: {thread.get('thread_id')}")
                st.write(f"**Subject:** {thread.get('subject')} | **Status:** {thread.get('status')}")

                # Timeline
                for email in thread.get("emails", []):
                    sentiment = email.get("sentiment") or "Neutral"
                    icon = SENTIMENT_COLOR.get(sentiment, "⚪")
                    urgency = email.get("urgency") or "—"
                    urg_icon = URGENCY_COLOR.get(urgency, "⚪")
                    cat = email.get("category") or "—"

                    with st.expander(f"{icon} Email #{email['id']} — {email.get('subject', '')} [{cat}] {urg_icon}"):
                        st.write(f"**Category:** {cat}")
                        st.write(f"**Urgency:** {urgency}")
                        st.write(f"**Sentiment:** {sentiment}")

                        # Process / Dry Run buttons
                        c1, c2 = st.columns(2)
                        with c1:
                            if st.button(f"🤖 Process", key=f"tw_proc_{email['id']}"):
                                with st.spinner("Agent running..."):
                                    status_code, result = safe_post(f"{API_BASE}/process-email/{email['id']}")
                                    if status_code == 200:
                                        st.success("Processed")

                                        # Agent Reasoning Panel
                                        st.subheader("🧠 Agent Reasoning Trace")
                                        for step in result.get("reasoning_trace", []):
                                            st.markdown(f"**Step {step.get('step')}** — `{step.get('action')}`")
                                            st.write(f"💭 **Thought:** {step.get('thought')}")
                                            if step.get("observation"):
                                                st.write(f"👁 **Observation:** {step.get('observation')}")

                                        # RAG context
                                        st.subheader("📚 RAG Policy Sources")
                                        st.write(result.get("rag_policy_sources", "—"))

                                        st.subheader("📝 Draft Reply")
                                        draft = result.get("draft_reply")
                                        if draft:
                                            st.text_area("Draft", draft, height=150)
                                        else:
                                            st.warning("No auto-reply generated (requires human or critical/security/legal category)")
                                    else:
                                        st.error(str(result))
                        with c2:
                            if st.button(f"🔍 Dry Run", key=f"tw_dry_{email['id']}"):
                                with st.spinner("Planning..."):
                                    status_code, result = safe_post(f"{API_BASE}/agent/dry-run/{email['id']}")
                                    if status_code == 200:
                                        st.info("DRY RUN — plan only")
                                        st.json(result.get("reasoning_trace", []))

                st.divider()


# =====================================
# PAGE 3 — ANALYTICS DASHBOARD
# =====================================

elif page == "📊 Analytics":

    st.title("📊 Analytics Dashboard")

    days = st.slider("Days to analyse", 7, 90, 30)

    col1, col2 = st.columns(2)

    # Category Distribution
    with col1:
        st.subheader("Email Categories")
        cat_data = safe_get(f"{API_BASE}/dashboard/categories", [])
        if cat_data:
            df_cat = pd.DataFrame(cat_data)
            df_cat = df_cat[df_cat["category"].notna()]
            if not df_cat.empty:
                fig = px.pie(df_cat, values="count", names="category", title="Category Distribution")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No classified emails yet.")
        else:
            st.info("No data.")

    # Sentiment Distribution
    with col2:
        st.subheader("Sentiment Distribution")
        sent_data = safe_get(f"{API_BASE}/dashboard/sentiment", [])
        if sent_data:
            df_sent = pd.DataFrame(sent_data)
            df_sent = df_sent[df_sent["sentiment"].notna()]
            if not df_sent.empty:
                fig = px.bar(
                    df_sent, x="sentiment", y="count",
                    title="Sentiment Analysis",
                    color="sentiment",
                    color_discrete_map={
                        "Positive": "green", "Neutral": "yellow",
                        "Negative": "red", "Mixed": "orange"
                    }
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No sentiment data yet.")
        else:
            st.info("No data.")

    # Ticket Priorities
    st.subheader("Ticket Priorities")
    ticket_data = safe_get(f"{API_BASE}/dashboard/tickets", [])
    if ticket_data:
        df_ticket = pd.DataFrame(ticket_data)
        if not df_ticket.empty:
            fig = px.bar(df_ticket, x="priority", y="count", title="Ticket Priority Distribution",
                         color="priority",
                         color_discrete_map={"Critical": "red", "High": "orange", "Medium": "yellow", "Low": "green"})
            st.plotly_chart(fig, use_container_width=True)

    # Sentiment Trend
    st.subheader("Sentiment Trend Over Time")
    sender_filter = st.text_input("Filter by sender (optional)", key="trend_sender")
    trend_url = f"{API_BASE}/analytics/sentiment-trend?days={days}"
    if sender_filter:
        trend_url += f"&sender={sender_filter}"

    trend_data = safe_get(trend_url, {})
    trend_points = trend_data.get("trend_data", []) if isinstance(trend_data, dict) else []

    if trend_points:
        df_trend = pd.DataFrame(trend_points)
        df_trend = df_trend[df_trend["sentiment_score"].notna()]
        if not df_trend.empty:
            fig = px.line(
                df_trend, x="timestamp", y="sentiment_score",
                color="sender", title="Sentiment Score Over Time",
                markers=True
            )
            fig.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="Neutral")
            fig.add_hline(y=-0.3, line_dash="dot", line_color="red", annotation_text="Negative threshold")
            st.plotly_chart(fig, use_container_width=True)

    # Deterioration Alerts
    alerts = trend_data.get("deterioration_alerts", []) if isinstance(trend_data, dict) else []
    if alerts:
        st.subheader("⚠️ Sentiment Deterioration Alerts")
        for alert in alerts:
            st.error(f"🔴 {alert['sender']}: {alert['alert']}")


# =====================================
# PAGE 4 — RAG DEBUG
# =====================================

elif page == "🔍 RAG Debug":

    st.title("🔍 RAG Knowledge Base Debug")

    query = st.text_input("Search knowledge base", placeholder="e.g. GDPR data portability 30 days")
    top_k = st.slider("Top K results", 1, 10, 5)

    if query:
        with st.spinner("Searching..."):
            results = safe_get(f"{API_BASE}/rag/search?q={query}&top_k={top_k}", {})

        if results and results.get("results"):
            st.success(f"Found {len(results['results'])} chunks")
            for r in results["results"]:
                with st.expander(f"#{r['rank']} — {r['source_doc']} (distance: {r['similarity_distance']})"):
                    st.write(r["chunk_text"])
        else:
            st.info("No results. Make sure the knowledge base is seeded (run rag/create_kb.py).")


# =====================================
# PAGE 5 — BULK OPERATIONS
# =====================================

elif page == "⚙️ Bulk Operations":

    st.title("⚙️ Bulk Operations")

    st.subheader("🚀 Process All Emails")
    st.write("Runs the AI triage agent on all emails in the database. This may take several minutes.")

    if st.button("▶️ Process All Emails with AI Agent"):
        progress = st.progress(0, text="Starting...")
        with st.spinner("Processing emails..."):
            status_code, result = safe_post(f"{API_BASE}/process-all-emails")
            progress.progress(100, text="Done!")
            if status_code == 200:
                st.success(f"✅ Processed {result['processed']} / {result['total']} emails")
                if result.get("errors"):
                    st.warning(f"⚠️ {len(result['errors'])} errors")
                    with st.expander("View errors"):
                        st.json(result["errors"])
            else:
                st.error(f"Failed: {result}")

    st.divider()

    st.subheader("🔢 Process Single Email")
    email_id = st.number_input("Email ID", min_value=1, step=1)

    col_proc, col_dry = st.columns(2)

    with col_proc:
        if st.button("🤖 Process Email (Live)"):
            with st.spinner("Agent processing..."):
                status_code, result = safe_post(f"{API_BASE}/process-email/{email_id}")
                if status_code == 200:
                    st.success("✅ Processed")
                    st.subheader("Classification")
                    st.json(result.get("classification", {}))
                    st.subheader("🧠 Reasoning Trace")
                    for step in result.get("reasoning_trace", []):
                        st.markdown(f"**Step {step.get('step')}** — `{step.get('action')}`")
                        st.caption(f"💭 {step.get('thought')}")
                        if step.get("observation"):
                            st.write(f"👁 {step.get('observation')}")
                    st.subheader("Actions Taken")
                    st.json(result.get("actions", []))
                    if result.get("draft_reply"):
                        st.subheader("📝 Draft Reply")
                        st.text_area("", result["draft_reply"], height=150)
                    else:
                        st.info("No auto-reply (critical/security/legal email — human required)")
                else:
                    st.error(f"Error: {result}")

    with col_dry:
        if st.button("🔍 Dry Run (Plan Only)"):
            with st.spinner("Planning..."):
                status_code, result = safe_post(f"{API_BASE}/agent/dry-run/{email_id}")
                if status_code == 200:
                    st.info("🔍 DRY RUN — No actions executed")
                    st.subheader("Planned Classification")
                    st.json(result.get("classification", {}))
                    st.subheader("Planned Actions")
                    st.json(result.get("actions", []))
                    st.subheader("Reasoning Trace")
                    st.json(result.get("reasoning_trace", []))
                else:
                    st.error(str(result))
