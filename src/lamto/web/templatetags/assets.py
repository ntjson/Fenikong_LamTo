"""Content-addressed URLs for the CSS and JS the workspace ships.

``{% static %}`` alone gives a stable URL, and the responses carry no
``Cache-Control`` or ``ETag`` — only ``Last-Modified``. A browser is then free
to heuristically reuse a stale copy without revalidating, which silently
serves an old ``staff.js`` against freshly rendered markup: the buttons are
there, the handlers are not, and clicking does nothing at all.

``{% asset %}`` appends a short digest of the file's current bytes, so the URL
changes whenever the file does and any cached copy is addressed by its old,
now-unused URL. Digests are memoised per path and recomputed when the file's
mtime moves, which keeps a dev edit visible on the next reload.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

from django import template
from django.contrib.staticfiles import finders
from django.templatetags.static import static

register = template.Library()

DIGEST_LENGTH = 12

_digests: dict[str, tuple[int, str]] = {}


def _absolute_path(path: str) -> str | None:
    found = finders.find(path)
    if isinstance(found, (list, tuple)):
        found = found[0] if found else None
    return found


def _digest(path: str) -> str | None:
    """Short content digest, or None when the file is not on this machine.

    Collected static served from object storage has no local file to read;
    returning None there degrades to the plain URL rather than raising.
    """
    absolute = _absolute_path(path)
    if not absolute:
        return None
    try:
        stamp = os.stat(absolute).st_mtime_ns
    except OSError:
        return None
    cached = _digests.get(path)
    if cached is not None and cached[0] == stamp:
        return cached[1]
    try:
        content = Path(absolute).read_bytes()
    except OSError:
        return None
    digest = hashlib.sha256(content).hexdigest()[:DIGEST_LENGTH]
    _digests[path] = (stamp, digest)
    return digest


@register.simple_tag
def asset(path: str) -> str:
    url = static(path)
    digest = _digest(path)
    if digest is None:
        return url
    separator = "&" if "?" in url else "?"
    return f"{url}{separator}v={digest}"
