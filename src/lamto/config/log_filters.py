"""Logging filters that must load before Django apps are ready.

Keep this free of model/ORM imports so LOGGING dictConfig can resolve it during
settings setup (spec 3.6: never log signed download tokens).
"""

from __future__ import annotations

import logging
import re

# Path segment under /api/v1/documents/<token>.
_DOWNLOAD_TOKEN_IN_TEXT = re.compile(r"(/api/v1/documents/)([^/?\s#\"']+)")


def scrub_download_token_in_text(text: str) -> str:
    """Replace the signed download path token with a constant redaction marker."""
    if not text:
        return text
    return _DOWNLOAD_TOKEN_IN_TEXT.sub(r"\1[redacted]", text)


class DownloadTokenLogFilter(logging.Filter):
    """Never leave a raw download token in a formatted log message."""

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            message = record.getMessage()
        except Exception:
            return True
        scrubbed = scrub_download_token_in_text(message)
        if scrubbed != message:
            record.msg = scrubbed
            record.args = ()
        return True
