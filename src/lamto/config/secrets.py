"""Env secret helpers used at settings load and by opt-in chain tests.

Keep this module free of Django app imports so settings can use it safely.
"""

from __future__ import annotations


def coalesce_secret(value: str | None, default: str = "") -> str:
    """Treat missing, empty, and whitespace-only values as unset.

    Operators often leave ``BLOCKCHAIN_*_PRIVATE_KEY=`` blank in ``.env.example``
    or fill with spaces; neither is a valid private key.
    """
    return (value or "").strip() or default
