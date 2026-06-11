# Service Level Agreement (SLA) Policy

## Uptime Commitment
- Target uptime: **99.9%** per calendar month (measured 24/7/365)
- Excludes: scheduled maintenance windows (notified 72h in advance), force majeure events

## Severity Levels & Response Times

### P0 — Critical (Complete Service Outage)
- Definition: Platform entirely unavailable; all customers affected
- Initial Response Time: **1 hour**
- Resolution Target: **4 hours**
- RCA Delivery: **24 hours** after resolution
- Credit: 10% of monthly fee per hour of downtime beyond 1 hour

### P1 — High (Major Functionality Affected)
- Definition: Core feature unavailable; significant customer impact
- Initial Response Time: **4 hours**
- Resolution Target: **8 hours**
- Credit: 5% of monthly fee per hour beyond 4 hours

### P2 — Medium (Minor Functionality Issue)
- Definition: Non-critical feature degraded; workaround available
- Initial Response Time: **24 hours**
- Resolution Target: **72 hours**
- No automatic credit; case-by-case review

### P3 — Low (General Inquiries / Cosmetic Issues)
- Initial Response Time: **48 hours**
- Resolution Target: **5 business days**

## SLA Credit Calculation
- Credits are calculated as a percentage of the **monthly subscription fee**
- Credits are applied to the **next invoice** — not issued as cash refunds
- Credit formula: `Credit = (Downtime Hours - SLA Threshold Hours) × Credit Rate × Monthly Fee`
- Maximum credit per incident: **30% of monthly fee**
- Maximum total credits per month: **50% of monthly fee**
- Credits must be **claimed within 30 days** of the incident

## How to Claim SLA Credits
1. Email support@platform.com with subject: "SLA Credit Request — [Incident Date]"
2. Include: incident timestamp, affected services, business impact description
3. Credits reviewed and confirmed within 5 business days
4. Credits automatically applied to next billing cycle

## Scheduled Maintenance
- Maintenance windows: Saturdays 02:00–04:00 UTC
- 72-hour advance notice provided via email and status page
- Downtime during scheduled maintenance does not count toward SLA

## Incident Communication
- Status page: status.platform.com (updated every 15 minutes during incidents)
- P0 incidents: email notification to all affected customers within 30 minutes
- RCA reports for P0 incidents delivered within 24 hours of resolution

## Enterprise SLA
- Enterprise customers may negotiate custom SLA terms
- Custom uptime targets up to 99.99% available
- Dedicated on-call engineer available for Enterprise tier
- SLA credits up to 100% of monthly fee for Enterprise customers

## Bob Jones / Enterprise Outage — October 2023 Reference
- Incident occurred: October 1, 2023, 08:50 UTC
- Duration: 47 minutes
- Severity: P0
- Affected tier: Enterprise
- SLA credit applicable: Customer entitled to credit per P0 credit formula
- RCA due: October 2, 2023 (24h after resolution)
