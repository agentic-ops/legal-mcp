"""PACER adapter (federal court records).

.. warning::

   PACER is a **paid** service. It bills per page, per document, or per
   search. Automated agents can issue many requests quickly and can
   exhaust a standard account's quarterly fee waiver in minutes. This
   integration is **disabled by default** and defaults to PACER's
   non-billable QA environment when enabled.

Two-step flow (see the PACER Authentication API User Guide):

1. **Authenticate** -- ``POST {auth}/services/cso-auth`` with a JSON body
   containing ``loginId`` and ``password`` (and optional ``clientCode`` /
   TOTP passcode). A successful response returns a ``nextGenCSO`` token.
2. **Search** -- reuse the ``nextGenCSO`` token as a cookie against the
   PACER Case Locator (PCL) API, e.g.
   ``POST {pcl}/pcl-public-api/rest/cases/find``.

Per PACER guidance, the token must be **reused** across requests; do not
re-authenticate on every call, as excessive auth calls can lead to
suspended access.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from integrations.config import PacerSettings, get_integration_settings
from utils import audit

AUTH_PATH = "/services/cso-auth"
PCL_FIND_PATH = "/pcl-public-api/rest/cases/find"

FEE_WARNING = (
    "PACER is a paid service and may incur per-page/per-search fees. "
    "Automated usage can exhaust a standard account's quarterly waiver "
    "quickly. Prefer CourtListener/RECAP where possible."
)


class PacerClient:
    """Thin, testable wrapper over the PACER Authentication + PCL APIs."""

    def __init__(
        self,
        settings: Optional[PacerSettings] = None,
        http_client: Any = None,
    ) -> None:
        self.settings = settings or get_integration_settings().pacer
        self._http_client = http_client
        self._token: Optional[str] = None

    @property
    def enabled(self) -> bool:
        return self.settings.enabled

    def status(self) -> Dict[str, Any]:
        """Return a non-sensitive status report (never leaks credentials)."""

        return {
            "source": "pacer",
            "enabled": self.settings.enabled,
            "configured": self.settings.configured,
            "environment": self.settings.environment,
            "auth_base_url": self.settings.auth_base_url,
            "pcl_base_url": self.settings.pcl_base_url,
            "missing_settings": self.settings.missing_settings(),
            "cost_warning": FEE_WARNING,
        }

    def _get_client(self):
        if self._http_client is not None:
            return self._http_client
        import httpx

        return httpx.Client(timeout=30.0)

    def authenticate(self, client: Any = None) -> Dict[str, Any]:
        """Obtain (and cache) a ``nextGenCSO`` token from PACER."""

        body: Dict[str, Any] = {
            "loginId": self.settings.login_id,
            "password": self.settings.password,
        }
        if self.settings.client_code:
            body["clientCode"] = self.settings.client_code
        if self.settings.otp_secret:
            # TOTP one-time passcode for accounts with 2FA enabled.
            body["otpCode"] = _totp(self.settings.otp_secret)

        client = client or self._get_client()
        response = client.post(
            f"{self.settings.auth_base_url}{AUTH_PATH}",
            json=body,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )
        response.raise_for_status()
        data = response.json()
        if str(data.get("loginResult")) != "0" or not data.get("nextGenCSO"):
            raise RuntimeError(
                "PACER authentication failed: "
                f"{data.get('errorDescription') or 'unknown error'}"
            )
        self._token = data["nextGenCSO"]
        return data

    def search(
        self, query: str, jurisdiction: Optional[str] = None, limit: int = 5
    ) -> Dict[str, Any]:
        """Search the PACER Case Locator; returns a structured dict."""

        audit(
            "pacer_search",
            query=query,
            jurisdiction=jurisdiction,
            enabled=self.settings.enabled,
        )
        if not self.settings.enabled:
            return {
                **self.status(),
                "query": query,
                "message": (
                    "PACER integration is disabled. Set PACER_ENABLED=true "
                    "to enable it (paid service; fees may apply)."
                ),
                "results": [],
            }
        if not self.settings.configured:
            return {
                **self.status(),
                "query": query,
                "message": (
                    "PACER is enabled but credentials are missing. Set "
                    + " and ".join(self.settings.missing_settings())
                    + "."
                ),
                "results": [],
            }

        try:
            client = self._get_client()
            if self._token is None:
                self.authenticate(client)
            response = client.post(
                f"{self.settings.pcl_base_url}{PCL_FIND_PATH}",
                json={"caseTitle": query},
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    # Reuse the nextGenCSO token as a cookie (per PACER
                    # guidance) without re-authenticating on each call.
                    "Cookie": f"NextGenCSO={self._token or ''}",
                },
            )
            response.raise_for_status()
            payload = response.json()
        except Exception as exc:  # pragma: no cover - network failure path
            return {
                **self.status(),
                "query": query,
                "error": f"PACER request failed: {exc}",
                "results": [],
            }

        content = payload.get("content", payload.get("results", []))
        return {
            "source": "pacer",
            "enabled": True,
            "environment": self.settings.environment,
            "query": query,
            "result_count": len(content),
            "results": content[:limit],
            "cost_warning": FEE_WARNING,
        }


def _totp(secret: str) -> str:
    """Generate a TOTP passcode from a base32 secret (RFC 6238).

    Implemented locally to avoid an extra dependency; used only when a
    PACER account has 2FA enabled and ``PACER_OTP_SECRET`` is provided.
    """

    import base64
    import hashlib
    import hmac
    import struct
    import time

    key = base64.b32decode(secret.strip().replace(" ", "").upper())
    counter = struct.pack(">Q", int(time.time()) // 30)
    digest = hmac.new(key, counter, hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    code = struct.unpack(">I", digest[offset : offset + 4])[0] & 0x7FFFFFFF
    return f"{code % 1_000_000:06d}"
