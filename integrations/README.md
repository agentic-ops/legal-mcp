# integrations/

Optional live legal-data integrations — disabled by default.

Every integration requires both a **feature flag** (an env var set to `true`) and **API credentials** before it becomes active. A fresh clone or fork makes **no network calls** unless you explicitly opt in.

## Modules

| Module | Purpose |
|--------|---------|
| `config.py` | `IntegrationSettings`, `PacerSettings`, `CourtListenerSettings` dataclasses; reads all env vars on demand via `get_integration_settings()` |
| `courtlistener.py` | HTTP adapter for the [CourtListener/RECAP REST API v4](https://www.courtlistener.com/help/api/rest/) — free, rate-limited, preferred live source |
| `pacer.py` | HTTP adapter for PACER (federal court records) — two-step auth (CSO token) against the PACER Case Locator API |
| `__init__.py` | Package init; re-exports `get_integration_settings` |

## Enabling CourtListener (free, preferred)

```bash
export COURTLISTENER_ENABLED=true
export COURTLISTENER_API_TOKEN="your-token"   # https://www.courtlistener.com/profile/api/
python main.py
```

| Variable | Default | Description |
|----------|---------|-------------|
| `COURTLISTENER_ENABLED` | `false` | Feature flag |
| `COURTLISTENER_API_TOKEN` | _(unset)_ | Token from your CourtListener profile |
| `COURTLISTENER_BASE_URL` | `https://www.courtlistener.com/api/rest/v4` | Override for testing |

## Enabling PACER (paid — read the warning below)

```bash
export PACER_ENABLED=true
export PACER_ENVIRONMENT=qa          # use qa for non-billable testing
export PACER_LOGIN_ID="your-username"
export PACER_PASSWORD="your-password"
python main.py
```

| Variable | Default | Description |
|----------|---------|-------------|
| `PACER_ENABLED` | `false` | Feature flag |
| `PACER_ENVIRONMENT` | `qa` | `qa` (non-billable) or `production` (billable) |
| `PACER_LOGIN_ID` | _(unset)_ | PACER username |
| `PACER_PASSWORD` | _(unset)_ | PACER password |
| `PACER_CLIENT_CODE` | _(unset)_ | Optional client/billing code |
| `PACER_OTP_SECRET` | _(unset)_ | Optional base32 TOTP secret if 2FA is enabled |

> **⚠️ PACER is a paid service.** AI agents can issue many requests per minute;
> a short agent session can exhaust a standard account's **$30 per quarter** fee waiver.
> Always start with `PACER_ENVIRONMENT=qa` (non-billable test environment).
> Register at [qa-pacer.uscourts.gov](https://qa-pacer.uscourts.gov) for a test account.
> **Never enable `PACER_ENVIRONMENT=production` in automated tests.**

Copy [`.env.example`](../.env.example) to `.env` for a template of all settings.

## Tests always mock the network

Integration tests use `httpx.MockTransport` so **no real network calls are made**, even when the feature flags appear enabled.
Keep new integration tests network-free the same way — never add tests that hit live PACER or CourtListener endpoints.

## Checking integration status at runtime

```bash
# Via the tool
integration_status

# Via the resource
legal://integrations
```

Both return only booleans and non-sensitive metadata — **credentials are never echoed back**.
