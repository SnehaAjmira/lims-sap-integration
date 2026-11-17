"""Environment configuration. Defaults run the service locally against a mock SAP client."""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    SAP_BASE_URL: str = os.getenv("SAP_BASE_URL", "")
    SAP_API_KEY: str = os.getenv("SAP_API_KEY", "")
    SAP_MODE: str = os.getenv("SAP_MODE", "mock")          # "mock" or "live"
    WEBHOOK_SECRET: str = os.getenv("WEBHOOK_SECRET", "")  # shared secret header; blank disables check
    AUDIT_LOG_PATH: str = os.getenv("AUDIT_LOG_PATH", "audit_log.jsonl")


settings = Settings()
