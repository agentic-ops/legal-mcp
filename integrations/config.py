"""Configuration for optional live legal-data integrations.

Every integration is controlled by two things:

1. A **feature flag** (an environment variable such as ``PACER_ENABLED``)
   that turns the integration on or off. All integrations default to
   **off** so that a fresh fork never makes surprise network calls or
   incurs fees.
2. **API credentials / keys** supplied via environment variables.

Settings are read from the environment on demand so that a running server
(or a test) can re-read them after changing an environment variable.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict, List, Optional

# PACER publishes separate QA (test, non-billable) and Production
# (billable) environments. The QA environment is the safe default.
PACER_ENVIRONMENTS: Dict[str, Dict[str, str]] = {
    "qa": {
        "auth": "https://qa-login.uscourts.gov",
        "pcl": "https://qa-pcl.uscourts.gov",
    },
    "production": {
        "auth": "https://pacer.login.uscourts.gov",
        "pcl": "https://pcl.uscourts.gov",
    },
}

COURTLISTENER_DEFAULT_BASE_URL = "https://www.courtlistener.com/api/rest/v4"


def _bool_env(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _opt_env(name: str) -> Optional[str]:
    value = os.environ.get(name)
    if value is None:
        return None
    value = value.strip()
    return value or None


@dataclass
class PacerSettings:
    """PACER feature flag + credentials.

    PACER is a *paid* service. Automated agents can consume a standard
    account's quarterly fee waiver quickly, so this integration is off by
    default and defaults to the non-billable QA environment when enabled.
    """

    enabled: bool = False
    environment: str = "qa"
    login_id: Optional[str] = None
    password: Optional[str] = None
    client_code: Optional[str] = None
    otp_secret: Optional[str] = None

    @classmethod
    def from_env(cls) -> "PacerSettings":
        environment = (os.environ.get("PACER_ENVIRONMENT", "qa") or "qa").lower()
        if environment not in PACER_ENVIRONMENTS:
            environment = "qa"
        return cls(
            enabled=_bool_env("PACER_ENABLED", False),
            environment=environment,
            login_id=_opt_env("PACER_LOGIN_ID"),
            password=_opt_env("PACER_PASSWORD"),
            client_code=_opt_env("PACER_CLIENT_CODE"),
            otp_secret=_opt_env("PACER_OTP_SECRET"),
        )

    @property
    def auth_base_url(self) -> str:
        return PACER_ENVIRONMENTS[self.environment]["auth"]

    @property
    def pcl_base_url(self) -> str:
        return PACER_ENVIRONMENTS[self.environment]["pcl"]

    @property
    def configured(self) -> bool:
        return bool(self.login_id and self.password)

    def missing_settings(self) -> List[str]:
        missing = []
        if not self.login_id:
            missing.append("PACER_LOGIN_ID")
        if not self.password:
            missing.append("PACER_PASSWORD")
        return missing


@dataclass
class CourtListenerSettings:
    """CourtListener / RECAP feature flag + API token.

    CourtListener is free (rate-limited) and is the preferred live source.
    It is still off by default so forks opt in explicitly.
    """

    enabled: bool = False
    base_url: str = COURTLISTENER_DEFAULT_BASE_URL
    api_token: Optional[str] = None

    @classmethod
    def from_env(cls) -> "CourtListenerSettings":
        return cls(
            enabled=_bool_env("COURTLISTENER_ENABLED", False),
            base_url=(
                os.environ.get(
                    "COURTLISTENER_BASE_URL", COURTLISTENER_DEFAULT_BASE_URL
                ).rstrip("/")
            ),
            api_token=_opt_env("COURTLISTENER_API_TOKEN"),
        )

    @property
    def configured(self) -> bool:
        return bool(self.api_token)

    def missing_settings(self) -> List[str]:
        return [] if self.api_token else ["COURTLISTENER_API_TOKEN"]


@dataclass
class IntegrationSettings:
    """Aggregate settings for all optional integrations."""

    pacer: PacerSettings
    courtlistener: CourtListenerSettings

    @classmethod
    def from_env(cls) -> "IntegrationSettings":
        return cls(
            pacer=PacerSettings.from_env(),
            courtlistener=CourtListenerSettings.from_env(),
        )


def get_integration_settings() -> IntegrationSettings:
    """Read the current integration settings from the environment."""

    return IntegrationSettings.from_env()
