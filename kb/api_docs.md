# API Documentation

## Authentication
- All API requests require Bearer Token authentication
- Header: `Authorization: Bearer <token>`
- Tokens issued via: POST /auth/token
- Token expiry: 24 hours; refresh via POST /auth/refresh

## Rate Limits by Tier

### Standard Plan
- 100 requests/minute
- 10,000 requests/day
- Burst: up to 200 req/min for 30 seconds

### Professional Plan
- 1,000 requests/minute
- 100,000 requests/day
- Burst: up to 2,000 req/min for 60 seconds

### Enterprise Plan
- Default: 5,000 requests/minute (customisable up to 10,000)
- Unlimited daily requests
- Dedicated rate limit pools available

## Rate Limit Headers
- `X-RateLimit-Limit`: Your plan's limit
- `X-RateLimit-Remaining`: Requests remaining in current window
- `X-RateLimit-Reset`: Unix timestamp when limit resets
- HTTP 429 returned when limit exceeded

## API v1 — DEPRECATED

> ⚠️ **API v1 is deprecated. Sunset date: December 31, 2023.**

- v1 endpoints: `/v1/*`
- v1 authentication: API Key in query param (`?api_key=...`)
- v1 response format: flat JSON objects
- After December 31, 2023: v1 endpoints will return HTTP 410 Gone

## API v2 — Current

- v2 endpoints: `/v2/*`
- **Breaking changes from v1:**
  1. **New auth header**: `Authorization: Bearer <token>` (no longer query param)
  2. **Required header**: `X-Workspace-ID: <workspace_id>` — ALL v2 requests require this header
  3. **Paginated responses**: List endpoints return `{ data: [...], pagination: { page, per_page, total } }`
  4. **Webhook signature validation**: HMAC-SHA256 signature in `X-Webhook-Signature` header required
  5. **ISO 8601 timestamps**: All timestamps now in ISO 8601 format (v1 used Unix epoch)
  6. **Nested error objects**: Errors return `{ error: { code, message, details } }` (v1 returned flat)

## Migration Guide (v1 → v2)
1. Generate new Bearer token via POST /auth/token
2. Add `X-Workspace-ID` header to all requests (find your Workspace ID in Settings → API)
3. Update pagination handling — v2 uses cursor-based pagination
4. Update webhook handler to validate HMAC-SHA256 signatures
5. Update timestamp parsing to ISO 8601
6. Test all integrations in staging before cutover
7. Reference: developer.platform.com/migration-guide

## Key Endpoints

### Emails
- `GET /v2/emails` — List emails (paginated)
- `POST /v2/emails` — Ingest email
- `GET /v2/emails/{id}` — Get email by ID
- `PATCH /v2/emails/{id}/status` — Update email status

### Webhooks (v2 only)
- `POST /v2/webhooks` — Register webhook
- Event types: `email.received`, `ticket.created`, `agent.decision`
- Signature: `X-Webhook-Signature: sha256=<hmac>`

### Tickets
- `GET /v2/tickets` — List tickets
- `POST /v2/tickets` — Create ticket
- `PATCH /v2/tickets/{id}` — Update ticket

## Common Errors
- `400 Bad Request` — Malformed payload or missing required fields
- `401 Unauthorized` — Missing or invalid Bearer token
- `403 Forbidden` — Valid token but insufficient permissions; check X-Workspace-ID
- `404 Not Found` — Resource does not exist
- `429 Too Many Requests` — Rate limit exceeded; check X-RateLimit-Reset header
- `500 Internal Server Error` — Platform error; contact support with request ID from `X-Request-ID` header
