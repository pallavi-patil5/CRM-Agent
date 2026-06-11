import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.heuristic_engine import HeuristicEngine
from services.email_classifier import EmailClassifier
from rag.retriever import search_knowledge_base


MAX_TOOL_CALLS = 6

NO_AUTO_REPLY_CATEGORIES = {
    "Security", "Legal", "Spam", "Internal"
}


class TriageAgent:

    def __init__(self):
        self.heuristic_engine = HeuristicEngine()
        self.classifier = EmailClassifier()

    # =============================================
    # TOOLS
    # =============================================

    def tool_get_thread_history(self, thread_id):
        """Fetch full thread context from DB."""
        try:
            from services.thread_service import ThreadService
            svc = ThreadService()
            history = svc.build_thread_history(thread_id)
            svc.close()
            return history or "No prior thread history found."
        except Exception as e:
            return f"Thread retrieval failed: {str(e)}"

    def tool_search_knowledge_base(self, query):
        """RAG search across internal knowledge base docs."""
        try:
            results = search_knowledge_base(query, top_k=3)
            if not results:
                return "No relevant knowledge base chunks found."
            return "\n\n---\n\n".join([
                f"[{r['source_doc']}] (distance: {r['distance']:.4f})\n{r['chunk_text']}"
                for r in results
            ])
        except Exception as e:
            return f"Knowledge base search failed: {str(e)}"

    def tool_create_ticket(self, classification, email_subject):
        """Create a support ticket from classification."""
        return {
            "ticket_created": True,
            "priority": classification.get("urgency", "Medium"),
            "title": f"{classification.get('category', 'Support')} — {email_subject[:60]}",
            "assignee": "Support Team"
        }

    def tool_escalate_to_human(self, reason, classification, thread_summary=""):
        """Escalate email to human with pre-filled brief."""
        return {
            "escalated": True,
            "reason": reason,
            "brief": {
                "category": classification.get("category"),
                "urgency": classification.get("urgency"),
                "sentiment": classification.get("sentiment"),
                "sentiment_score": classification.get("sentiment_score"),
                "confidence": classification.get("confidence"),
                "thread_summary": thread_summary,
                "escalation_reason": classification.get("escalation_reason", reason)
            }
        }

    def tool_flag_legal(self, email_subject, reason="Legal threat detected"):
        """Route email to legal team with context summary."""
        return {
            "legal_flag": True,
            "routed_to": "legal@platform.com",
            "cc": "ceo@platform.com",
            "reason": reason,
            "subject": email_subject,
            "instruction": "Do NOT respond to customer — legal team handles all communication"
        }

    def tool_flag_security(self, email_subject, threat_type="Security threat"):
        """Route email to security team."""
        return {
            "security_flag": True,
            "routed_to": "security@platform.com",
            "cc": "cto@platform.com",
            "threat_type": threat_type,
            "subject": email_subject,
            "instruction": "Do NOT auto-reply to attacker. Preserve all email headers as evidence."
        }

    def tool_flag_compliance(self, email_subject, compliance_type="Compliance request"):
        """Flag GDPR/HIPAA/compliance requests to compliance team."""
        return {
            "compliance_flag": True,
            "routed_to": "compliance@platform.com",
            "compliance_type": compliance_type,
            "subject": email_subject,
            "instruction": "Send acknowledgement citing 30-day statutory window. Do NOT send generic reply."
        }

    def tool_draft_reply(self, classification, rag_context=""):
        """Draft a contextual reply based on category and RAG context."""
        category = classification.get("category", "General Inquiry")
        urgency = classification.get("urgency", "Medium")

        # Never draft for these categories
        if category in NO_AUTO_REPLY_CATEGORIES or urgency == "Critical":
            return None

        if classification.get("suggested_reply"):
            return classification["suggested_reply"]

        templates = {
            "Refund": (
                "Thank you for contacting us regarding your refund request. "
                "We have received your request and our billing team is reviewing it. "
                "Per our refund policy, approved refunds are processed within 7 business days. "
                "We will follow up with you shortly."
            ),
            "Bug Report": (
                "Thank you for reporting this issue. We have logged it with our engineering team "
                "and assigned it for immediate investigation. We will keep you updated on the resolution."
            ),
            "Feature Request": (
                "Thank you for your suggestion! We have shared it with our product team for review. "
                "We appreciate your feedback as it helps us improve the platform."
            ),
            "Complaint": (
                "We sincerely apologize for your experience. Your concern has been escalated to our "
                "senior customer success team who will reach out to you personally within 4 hours."
            ),
            "Billing": (
                "Thank you for reaching out about your billing inquiry. Our billing team is reviewing "
                "your account and will respond with a full explanation within 24 hours."
            ),
            "Compliance": (
                "We have received your compliance request. Our compliance team will respond "
                "within the statutory timeframe. You will receive a formal acknowledgement shortly."
            ),
            "General Inquiry": (
                "Thank you for contacting us. We have received your inquiry and will respond "
                "within 1-2 business days."
            )
        }

        return templates.get(category, "Thank you for contacting support. We will respond shortly.")

    # =============================================
    # REACT AGENT LOOP
    # =============================================

    def process_email(self, email_data, dry_run=False):
        """
        ReAct loop: Thought → Action → Observation → Repeat (max 6 tool calls)
        Returns structured result with full reasoning trace.
        """
        reasoning_trace = []
        actions_taken = []
        tool_calls = 0

        subject = email_data.get("subject", "")
        body = email_data.get("body", "")
        thread_id = email_data.get("thread_id", "")

        # Truncate body if too long (>10000 chars)
        if len(body) > 10000:
            body = body[:10000] + "\n[TRUNCATED — original body exceeded 10,000 characters]"

        # -----------------------------------------------
        # STEP 1: Heuristic pre-filter (synchronous, fast)
        # -----------------------------------------------
        reasoning_trace.append({
            "step": 1,
            "thought": "Run heuristic pre-filter to detect spam, security, legal, and urgency signals before LLM call.",
            "action": "heuristic_analysis",
            "observation": None
        })

        heuristic_result = self.heuristic_engine.analyze_email(subject, body)
        reasoning_trace[-1]["observation"] = heuristic_result

        # Hard exits on heuristic — no LLM needed
        if heuristic_result.get("spam"):
            reasoning_trace.append({
                "step": 2,
                "thought": "Heuristic detected spam. No LLM classification needed. No auto-reply. Marking as Spam.",
                "action": "mark_spam",
                "observation": "Email routed to spam. No further action."
            })
            return self._build_result(
                classification={
                    "category": "Spam",
                    "sentiment": "Neutral",
                    "sentiment_score": 0.0,
                    "urgency": "Low",
                    "requires_human": False,
                    "escalation_reason": None,
                    "suggested_reply": None,
                    "confidence": 0.99,
                    "reasoning": "Heuristic spam detection triggered.",
                    "detected_entities": {"order_ids": [], "ticket_ids": [], "monetary_amounts": [], "deadlines": [], "products_mentioned": []}
                },
                actions=actions_taken,
                draft_reply=None,
                reasoning_trace=reasoning_trace,
                dry_run=dry_run
            )

        # -----------------------------------------------
        # STEP 2: Retrieve thread history
        # -----------------------------------------------
        tool_calls += 1
        reasoning_trace.append({
            "step": 2,
            "thought": f"Retrieve full thread history for thread_id={thread_id} to provide complete context before classification.",
            "action": "tool_get_thread_history",
            "input": thread_id,
            "observation": None
        })

        thread_history = self.tool_get_thread_history(thread_id)
        reasoning_trace[-1]["observation"] = f"Thread history retrieved ({len(thread_history)} chars)"

        # -----------------------------------------------
        # STEP 3: RAG search
        # -----------------------------------------------
        tool_calls += 1
        rag_query = f"{subject}\n{body[:500]}"
        reasoning_trace.append({
            "step": 3,
            "thought": "Search knowledge base for relevant policy context to ground the classification and reply.",
            "action": "tool_search_knowledge_base",
            "input": rag_query[:200],
            "observation": None
        })

        retrieved_chunks = search_knowledge_base(rag_query, top_k=3)
        rag_context = "\n\n".join([
            f"[{c['source_doc']}]\n{c['chunk_text']}"
            for c in retrieved_chunks
        ])
        reasoning_trace[-1]["observation"] = f"Retrieved {len(retrieved_chunks)} chunks: {[c['source_doc'] for c in retrieved_chunks]}"

        # -----------------------------------------------
        # STEP 4: LLM classification
        # -----------------------------------------------
        tool_calls += 1
        reasoning_trace.append({
            "step": 4,
            "thought": "Run LLM classification with full thread history and RAG context injected into prompt.",
            "action": "llm_classify",
            "observation": None
        })

        classification = self.classifier.classify(
            email_subject=subject,
            email_body=body,
            thread_history=thread_history,
            rag_context=rag_context
        )
        reasoning_trace[-1]["observation"] = {
            "category": classification.get("category"),
            "sentiment": classification.get("sentiment"),
            "urgency": classification.get("urgency"),
            "confidence": classification.get("confidence"),
            "requires_human": classification.get("requires_human")
        }

        category = classification.get("category", "General Inquiry")
        urgency = classification.get("urgency", "Medium")

        # -----------------------------------------------
        # STEP 5: Route based on classification
        # -----------------------------------------------

        # Security — immediate flag, no auto-reply, escalate
        if heuristic_result.get("security") or category == "Security":
            tool_calls += 1
            reasoning_trace.append({
                "step": 5,
                "thought": "Security threat detected. Must flag_security and escalate immediately. NEVER auto-reply.",
                "action": "tool_flag_security",
                "observation": None
            })
            security_action = self.tool_flag_security(subject, threat_type=category)
            actions_taken.append(security_action)
            reasoning_trace[-1]["observation"] = security_action

            if tool_calls < MAX_TOOL_CALLS:
                tool_calls += 1
                escalation = self.tool_escalate_to_human(
                    "Security incident — immediate escalation required",
                    classification, thread_history[:500]
                )
                actions_taken.append(escalation)
                reasoning_trace.append({
                    "step": 6,
                    "thought": "Escalate to human security team with full context brief.",
                    "action": "tool_escalate_to_human",
                    "observation": escalation
                })

            return self._build_result(classification, actions_taken, None, reasoning_trace, dry_run)

        # Legal — flag legal, no auto-reply, escalate
        if heuristic_result.get("legal") or category == "Legal":
            tool_calls += 1
            reasoning_trace.append({
                "step": 5,
                "thought": "Legal threat detected. Must flag_for_legal and escalate. NEVER auto-reply or admit liability.",
                "action": "tool_flag_legal",
                "observation": None
            })
            legal_action = self.tool_flag_legal(subject, reason=classification.get("escalation_reason", "Legal threat"))
            actions_taken.append(legal_action)
            reasoning_trace[-1]["observation"] = legal_action

            if tool_calls < MAX_TOOL_CALLS:
                tool_calls += 1
                escalation = self.tool_escalate_to_human(
                    "Legal threat — legal team review required",
                    classification, thread_history[:500]
                )
                actions_taken.append(escalation)
                reasoning_trace.append({
                    "step": 6,
                    "thought": "Escalate to legal team with pre-filled brief. No customer-facing reply.",
                    "action": "tool_escalate_to_human",
                    "observation": escalation
                })

            return self._build_result(classification, actions_taken, None, reasoning_trace, dry_run)

        # Compliance (GDPR/HIPAA) — flag compliance, acknowledgement only
        if heuristic_result.get("compliance") or category == "Compliance":
            tool_calls += 1
            reasoning_trace.append({
                "step": 5,
                "thought": "Compliance request (GDPR/HIPAA) detected. Flag to compliance team. Send acknowledgement citing statutory window. Do NOT send generic reply.",
                "action": "tool_flag_compliance",
                "observation": None
            })
            compliance_action = self.tool_flag_compliance(subject, compliance_type=category)
            actions_taken.append(compliance_action)
            reasoning_trace[-1]["observation"] = compliance_action

            if tool_calls < MAX_TOOL_CALLS:
                tool_calls += 1
                escalation = self.tool_escalate_to_human(
                    "Compliance request — legal obligation to respond within statutory timeframe",
                    classification
                )
                actions_taken.append(escalation)
                reasoning_trace.append({
                    "step": 6,
                    "thought": "Escalate to compliance team and create compliance ticket.",
                    "action": "tool_escalate_to_human",
                    "observation": escalation
                })

            return self._build_result(classification, actions_taken, None, reasoning_trace, dry_run)

        # Critical urgency — always escalate, never auto-reply
        if urgency == "Critical":
            tool_calls += 1
            reasoning_trace.append({
                "step": 5,
                "thought": "Critical urgency detected. Agent must NOT auto-reply. Escalate to human immediately.",
                "action": "tool_escalate_to_human",
                "observation": None
            })
            escalation = self.tool_escalate_to_human(
                f"Critical urgency email — {category}",
                classification, thread_history[:500]
            )
            actions_taken.append(escalation)
            reasoning_trace[-1]["observation"] = escalation

            if tool_calls < MAX_TOOL_CALLS and category in ["Complaint", "Refund", "Bug Report"]:
                tool_calls += 1
                ticket = self.tool_create_ticket(classification, subject)
                actions_taken.append(ticket)
                reasoning_trace.append({
                    "step": 6,
                    "thought": "Create support ticket to track this critical issue.",
                    "action": "tool_create_ticket",
                    "observation": ticket
                })

            return self._build_result(classification, actions_taken, None, reasoning_trace, dry_run)

        # Requires human review (low confidence or flagged)
        if classification.get("requires_human"):
            tool_calls += 1
            reasoning_trace.append({
                "step": 5,
                "thought": f"Email requires human review: {classification.get('escalation_reason', 'Flagged by classifier')}. Escalating.",
                "action": "tool_escalate_to_human",
                "observation": None
            })
            escalation = self.tool_escalate_to_human(
                classification.get("escalation_reason", "Human review required"),
                classification
            )
            actions_taken.append(escalation)
            reasoning_trace[-1]["observation"] = escalation

            if tool_calls < MAX_TOOL_CALLS and category in ["Complaint", "Refund", "Bug Report", "Billing"]:
                tool_calls += 1
                ticket = self.tool_create_ticket(classification, subject)
                actions_taken.append(ticket)
                reasoning_trace.append({
                    "step": 6,
                    "thought": "Create support ticket to track issue requiring human handling.",
                    "action": "tool_create_ticket",
                    "observation": ticket
                })

            return self._build_result(classification, actions_taken, None, reasoning_trace, dry_run)

        # Standard handling — create ticket if applicable, draft reply
        if category in ["Complaint", "Refund", "Bug Report", "Billing"]:
            tool_calls += 1
            reasoning_trace.append({
                "step": 5,
                "thought": f"Category is {category}. Creating support ticket.",
                "action": "tool_create_ticket",
                "observation": None
            })
            ticket = self.tool_create_ticket(classification, subject)
            actions_taken.append(ticket)
            reasoning_trace[-1]["observation"] = ticket

        # Draft reply
        if tool_calls < MAX_TOOL_CALLS:
            tool_calls += 1
            reasoning_trace.append({
                "step": tool_calls,
                "thought": "Draft contextual reply using RAG context and classification result.",
                "action": "tool_draft_reply",
                "observation": None
            })
            draft = self.tool_draft_reply(classification, rag_context)
            reasoning_trace[-1]["observation"] = f"Draft reply generated ({len(draft or '')} chars)"
        else:
            # Max tool calls reached — escalate
            reasoning_trace.append({
                "step": tool_calls + 1,
                "thought": "Maximum tool calls (6) reached without resolution. Escalating to human.",
                "action": "tool_escalate_to_human",
                "observation": "Max steps exceeded"
            })
            escalation = self.tool_escalate_to_human(
                "Agent reached maximum tool call limit without resolution",
                classification
            )
            actions_taken.append(escalation)
            draft = None

        return self._build_result(classification, actions_taken, draft, reasoning_trace, dry_run)

    # =============================================
    # RESULT BUILDER
    # =============================================

    def _build_result(self, classification, actions, draft_reply, reasoning_trace, dry_run=False):
        return {
            "mode": "DRY_RUN" if dry_run else "LIVE",
            "classification": classification,
            "actions": actions,
            "draft_reply": draft_reply,
            "reasoning_trace": reasoning_trace,
            "rag_policy_sources": self._extract_policy_sources(reasoning_trace)
        }

    def _extract_policy_sources(self, reasoning_trace):
        """Extract which KB docs were cited in this agent run."""
        for step in reasoning_trace:
            if step.get("action") == "tool_search_knowledge_base":
                obs = step.get("observation", "")
                if isinstance(obs, str) and "chunks" in obs:
                    return obs
        return []


# =============================================
# TEST
# =============================================

if __name__ == "__main__":

    agent = TriageAgent()

    sample_email = {
        "thread_id": "thread_bob_outage",
        "subject": "Escalation: SLA Breach + Legal Review",
        "body": (
            "We have reviewed the October 1st incident report you provided. "
            "The RCA is inadequate — it does not address the root cause or corrective actions. "
            "Our legal team is now involved. Please expect formal correspondence. "
            "We are also putting the renewal on hold pending resolution."
        )
    }

    result = agent.process_email(sample_email)
    print(json.dumps(result, indent=2))
