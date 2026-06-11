import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import ollama


class EmailClassifier:

    def build_prompt(
        self,
        email_subject,
        email_body,
        thread_history="",
        rag_context=""
    ):

        return f"""You are an expert customer support AI for a B2B SaaS platform.

Analyze the email carefully using the full thread history and knowledge base context provided.

THREAD HISTORY:
{thread_history if thread_history else "No prior thread history."}

KNOWLEDGE BASE CONTEXT:
{rag_context if rag_context else "No knowledge base context retrieved."}

CURRENT EMAIL SUBJECT:
{email_subject}

CURRENT EMAIL BODY:
{email_body}

INSTRUCTIONS:
- Analyze the full thread context before classifying
- If signals conflict (e.g. positive tone but refund request), resolve and note in reasoning
- confidence below 0.70 MUST set requires_human=true
- NEVER suggest auto-reply for: Security, Legal, Compliance, Spam, or Critical urgency emails
- Extract all named entities (order IDs, ticket IDs, monetary amounts, deadlines, products)
- sentiment_score: float from -1.0 (very negative) to +1.0 (very positive)

Return ONLY valid JSON matching this exact schema. No markdown, no explanation, no text outside JSON.

{{
  "category": "Complaint|Billing|Refund|Bug Report|Feature Request|Security|Legal|Compliance|Sales|Spam|Internal|General Inquiry",
  "sentiment": "Positive|Neutral|Negative|Mixed",
  "sentiment_score": 0.0,
  "urgency": "Critical|High|Medium|Low",
  "requires_human": false,
  "escalation_reason": null,
  "suggested_reply": null,
  "confidence": 0.0,
  "reasoning": "",
  "detected_entities": {{
    "order_ids": [],
    "ticket_ids": [],
    "monetary_amounts": [],
    "deadlines": [],
    "products_mentioned": []
  }}
}}

Rules:
- escalation_reason: fill if requires_human=true, else null
- suggested_reply: fill if requires_human=false AND category NOT in [Security, Legal, Spam, Internal], else null
- For conflicting signals: pick the highest-severity category, note conflict in reasoning
- Return ONLY JSON.
"""

    def classify(
        self,
        email_subject,
        email_body,
        thread_history="",
        rag_context=""
    ):

        prompt = self.build_prompt(
            email_subject,
            email_body,
            thread_history,
            rag_context
        )

        response = ollama.chat(
            model="llama3",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        content = response["message"]["content"]

        try:
            start = content.find("{")
            end = content.rfind("}") + 1
            json_text = content[start:end]
            result = json.loads(json_text)

            # Enforce: low confidence → requires human
            if result.get("confidence", 1.0) < 0.70:
                result["requires_human"] = True
                if not result.get("escalation_reason"):
                    result["escalation_reason"] = "Low confidence classification — requires human review"

            # Enforce: never suggest auto-reply for critical/security/legal/spam
            if result.get("urgency") == "Critical" or result.get("category") in [
                "Security", "Legal", "Compliance", "Spam", "Internal"
            ]:
                result["requires_human"] = True
                result["suggested_reply"] = None

            return result

        except Exception as e:
            return {
                "category": "General Inquiry",
                "sentiment": "Neutral",
                "sentiment_score": 0.0,
                "urgency": "Medium",
                "requires_human": True,
                "escalation_reason": f"Classification parsing error: {str(e)}",
                "suggested_reply": None,
                "confidence": 0.0,
                "reasoning": f"Failed to parse LLM response: {str(e)}",
                "detected_entities": {
                    "order_ids": [],
                    "ticket_ids": [],
                    "monetary_amounts": [],
                    "deadlines": [],
                    "products_mentioned": []
                }
            }


if __name__ == "__main__":

    classifier = EmailClassifier()

    result = classifier.classify(
        email_subject="Refund Request - Order #88271",
        email_body="I am extremely unhappy. The dashboard has been slow for 3 days. I want a full refund immediately."
    )

    print(json.dumps(result, indent=4))
