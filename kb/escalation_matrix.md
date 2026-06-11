# Escalation Matrix

## Legal Threats

### Trigger Conditions
- Lawsuit threats or mentions of attorney involvement
- Cease and desist notices
- Trademark/IP infringement claims
- Formal legal notices or court filings
- Regulatory legal action threats

### Routing
- **Immediate action required (within 1 hour)**
- Route to: legal@platform.com
- CC: ceo@platform.com
- Do NOT respond to customer — legal team handles all communication
- Flag email as Legal in CRM with `flag_for_legal` action
- Create compliance ticket with full thread history attached
- Never admit liability or make commitments in written communication

---

## Security Incidents

### Trigger Conditions
- Ransomware threats or demands
- Reports of data breach or exfiltration
- Suspicious login alerts from unknown locations
- Threats to publish customer data
- Requests for Bitcoin/crypto payment under threat
- Hacking claims or unauthorized access reports

### Routing
- **Immediate escalation — within 15 minutes**
- Route to: security@platform.com
- CC: cto@platform.com, legal@platform.com
- Do NOT auto-reply to attacker — silence is the correct response
- Preserve all email headers and metadata as evidence
- Trigger incident response protocol
- Notify affected customers within 72 hours (GDPR Article 33 obligation)

---

## Compliance & Regulatory

### Trigger Conditions
- GDPR data subject requests (Articles 15, 17, 20)
- HIPAA inquiries or BAA requests
- SOC 2 / ISO 27001 audit requests
- Government or regulatory body inquiries
- Privacy complaints

### Routing
- Route to: compliance@platform.com
- Response SLA: 24 hours (acknowledgement), 30 days (resolution for GDPR)
- Auto-acknowledgement must cite statutory response window
- Create compliance ticket and assign to DPO (Data Protection Officer)

---

## VIP / Enterprise Churn Risk

### Trigger Conditions
- Enterprise customer threatening to cancel
- VIP account with 2+ unanswered support emails
- Customer threatening public reviews (G2, Trustpilot, Twitter/X, Capterra)
- Account value > $2,000/month and negative sentiment trend
- Customer requesting refund AND threatening reviews simultaneously

### Routing
- Route to: vip-support@platform.com
- CC: account-executive@platform.com, vp-success@platform.com
- Response SLA: 1 hour
- Recommended action: Proactive phone call + personalised email from VP of Customer Success
- Offer: Per retention playbook (see refund_policy.md)

---

## Public Reputation Threats

### Trigger Conditions
- Mentions of G2, Trustpilot, Capterra, Twitter, LinkedIn, Reddit
- Press or media inquiries
- Customer explicitly states intent to post negative review
- Influencer or journalist identified as sender

### Routing
- Route to: pr@platform.com + customer-success@platform.com
- Check current review scores before responding
- PR team reviews all public statements before sending
- Response SLA: 2 hours

---

## P0 Outage Escalation

### Trigger Conditions
- Complete platform unavailability reported by customer
- Multiple customers reporting same issue simultaneously
- Production system down with active financial impact

### Routing
- Route to: oncall@platform.com (24/7 pager)
- CC: engineering@platform.com, cto@platform.com
- SLA: 1-hour initial response, 4-hour resolution target
- RCA required within 24 hours of resolution

---

## GDPR Requests — Special Handling

### Article 20 Data Portability (Formal Request)
1. **Do NOT send generic auto-reply**
2. Send acknowledgement within 24 hours citing 30-day statutory window
3. Flag for Legal & Compliance team
4. Create compliance ticket with priority = High
5. Assign to DPO
6. Verify requestor identity before data export
7. Deliver export within 30 days in JSON/CSV format

---

## Bob Jones / Enterprise Outage — Escalation Reference
- Thread: thread_bob_outage
- Situation: P0 incident → SLA breach → legal escalation
- Required actions:
  1. Retrieve full thread history (4+ emails)
  2. Check SLA credit entitlement (47-minute P0 outage)
  3. Acknowledge RCA inadequacy
  4. flag_for_legal() — legal team involved per msg_060
  5. Draft empathetic holding reply citing SLA credit policy
  6. escalate_to_human() with pre-filled brief: account tier, renewal status, credit owed
  7. Do NOT make binding commitments about legal matters
