# RabbitMirror Web App

## Rate limiting
The JSON API under `/api/*` is protected by a lightweight in-memory rate limiter.

Configuration via environment variables:
- `API_RATE_LIMIT` (default 60): number of requests allowed per window per client and endpoint.
- `API_RATE_WINDOW` (default 60): window size in seconds.
- `API_RATE_LIMIT_BYPASS` (default 0): set to `1`/`true`/`yes` to bypass rate limiting (useful in tests or local debugging).

Identity for limiting is derived from `X-API-Key` when `API_KEY` is configured; otherwise, the client IP is used. Each endpoint is limited independently.
