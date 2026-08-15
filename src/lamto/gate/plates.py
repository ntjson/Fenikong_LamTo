"""Vietnamese licence plate normalization.

Plates are compared as one normalized string: uppercase, ASCII letters and
digits only. ``51F-123.45``, ``51f 123.45`` and ``51F12345`` are the same
plate. This is the only form the system stores or matches on; the raw text a
reader produced is kept separately on the event so a bad OCR read stays
visible.
"""

import re
import unicodedata

# Vietnamese plates are ASCII, but a reader or a keyboard can emit full-width
# or decorated characters; fold them before stripping.
_NON_ALNUM = re.compile(r"[^A-Z0-9]")

MIN_LENGTH = 5
MAX_LENGTH = 12


class PlateFormatError(ValueError):
    """Plate has no usable alphanumeric content, or an implausible length."""


def normalize_plate(raw: str | None) -> str:
    folded = unicodedata.normalize("NFKD", raw or "").upper()
    normalized = _NON_ALNUM.sub("", folded)
    if not MIN_LENGTH <= len(normalized) <= MAX_LENGTH:
        raise PlateFormatError(
            f"Plate must contain {MIN_LENGTH} to {MAX_LENGTH} letters or digits."
        )
    return normalized
