"""Guards that keep the staff workspace Vietnamese.

The workspace is fully translated, so the historical leak was never a missing
msgstr — it was LocaleMiddleware negotiating against LANGUAGES=[vi, en] and
resolving `en` for an English browser, which renders the English msgids.
"""

import pathlib
import re

from django.conf import settings
from django.test import SimpleTestCase
from django.utils.translation import get_language_from_request


class _FakeRequest:
    def __init__(self, *, accept_language=None, cookie=None):
        self.META = {}
        if accept_language is not None:
            self.META["HTTP_ACCEPT_LANGUAGE"] = accept_language
        self.COOKIES = {}
        if cookie is not None:
            self.COOKIES[settings.LANGUAGE_COOKIE_NAME] = cookie
        self.session = {}

    def get_full_path(self):
        return "/s/"


class LocaleLockTests(SimpleTestCase):
    def test_only_vietnamese_is_offered(self):
        assert [code for code, _label in settings.LANGUAGES] == ["vi"]

    def test_language_code_is_vietnamese(self):
        assert settings.LANGUAGE_CODE == "vi"

    def test_english_browser_still_gets_vietnamese(self):
        request = _FakeRequest(accept_language="en-US,en;q=0.9")
        assert get_language_from_request(request) == "vi"

    def test_english_cookie_still_gets_vietnamese(self):
        request = _FakeRequest(cookie="en")
        assert get_language_from_request(request) == "vi"

    def test_no_header_gets_vietnamese(self):
        assert get_language_from_request(_FakeRequest()) == "vi"


PO_PATH = pathlib.Path(settings.LOCALE_PATHS[0]) / "vi" / "LC_MESSAGES" / "django.po"

# Source roots the guards scan. Tests and migrations are excluded: test files
# legitimately assert English msgids, and migrations carry frozen historical
# strings that are never rendered.
SRC_ROOT = pathlib.Path(settings.BASE_DIR)

TRANS_TAG = re.compile(r"""\{%\s*trans(?:late)?\s+(["'])(.+?)\1""")
# Longest-first alternation: `gettext` would otherwise shadow `gettext_lazy`.
# The trailing class allows `)`, `,`, `}` and `]`. `)` closes an ordinary
# call — including a nested one, e.g. the `_(`'s own paren in
# ValidationError({"field": _("...")}) — and `,` covers a string followed by
# more arguments, e.g. ngettext's singular before its plural. `}`/`]` are
# extra headroom for other nested-literal shapes: a harmless superset, since
# a wider class can only match more, never hide a leak.
PY_CALL = re.compile(
    r"""\b(?:gettext_lazy|gettext|ngettext|_)\(\s*(["'])(.+?)\1\s*[,)}\]]"""
)


def po_entries(path):
    """Parse a .po file into entries, joining multi-line msgid/msgstr strings.

    A msgid_plural line gets its own key rather than being appended onto
    msgid, so an entry may carry msgid_plural alongside msgid/msgstr/fuzzy.

    Standard library only, deliberately: the guard must run wherever pytest
    runs, and this repository has no gettext toolchain installed.
    """
    entries = []
    current = {"msgid": "", "msgstr": "", "fuzzy": False}
    key = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            if current["msgid"] or current["msgstr"]:
                entries.append(current)
            current, key = {"msgid": "", "msgstr": "", "fuzzy": False}, None
            continue
        if line.startswith("#,") and "fuzzy" in line:
            current["fuzzy"] = True
            continue
        if line.startswith("#"):
            continue
        match = re.match(r'(msgid|msgstr|msgid_plural|msgstr\[\d+\])\s+"(.*)"$', line)
        if match:
            key = "msgstr" if match.group(1).startswith("msgstr") else match.group(1)
            current.setdefault(key, "")
            current[key] += match.group(2)
            continue
        if line.startswith('"') and line.endswith('"') and key:
            current[key] += line[1:-1]
    if current["msgid"] or current["msgstr"]:
        entries.append(current)
    return entries


class CatalogCompleteTests(SimpleTestCase):
    """Every msgid in the catalog has a Vietnamese translation."""

    def test_no_untranslated_or_fuzzy_entries(self):
        # The header entry has an empty msgid and carries metadata, not text.
        translatable = [e for e in po_entries(PO_PATH) if e["msgid"]]
        assert translatable, "catalog parsed as empty; the parser or path is wrong"
        broken = [
            e["msgid"] for e in translatable if not e["msgstr"] or e["fuzzy"]
        ]
        assert not broken, (
            f"{len(broken)} msgid(s) are untranslated or fuzzy and will render "
            f"English under vi: {broken[:5]}"
        )


class CatalogCurrentTests(SimpleTestCase):
    """Every translatable literal in the source has a msgid in the catalog.

    This catches the leak CatalogCompleteTests cannot: someone adds a
    {% trans %} tag or a _() call and never runs makemessages, so the string
    has no msgid at all and silently renders English under vi.

    Known limits, accepted: {% blocktrans %} blocks, calls split across
    lines, strings built at runtime, pgettext/npgettext calls, the
    gettext_noop/ngettext_lazy/pgettext_lazy wrappers, and ngettext's plural
    msgid are not covered. Full coverage needs xgettext, which is not
    installed here. This is a deliberate 90% check, not a replacement for
    makemessages.
    """

    def _missing(self):
        msgids = {e["msgid"] for e in po_entries(PO_PATH)}
        missing = []
        scanned = 0
        for path in SRC_ROOT.rglob("*.html"):
            scanned += 1
            text = path.read_text(encoding="utf-8")
            for match in TRANS_TAG.finditer(text):
                if match.group(2) not in msgids:
                    missing.append((str(path), match.group(2)))
        for path in SRC_ROOT.rglob("*.py"):
            # Relative to SRC_ROOT, not `"/tests/" in str(path)`: an absolute
            # checkout path containing "tests" (e.g. /home/ci/tests/lamto)
            # would otherwise match on the prefix and skip every .py file.
            if {"tests", "migrations"} & set(path.relative_to(SRC_ROOT).parts):
                continue
            scanned += 1
            text = path.read_text(encoding="utf-8")
            for match in PY_CALL.finditer(text):
                if match.group(2) not in msgids:
                    missing.append((str(path), match.group(2)))
        # `scanned` is ~210 (~170 .py + ~40 .html) on the current tree. A bare
        # `assert scanned` only catches zero; it would stay truthy through a
        # drastically truncated scan (e.g. SRC_ROOT resolving one level too
        # deep). 150 is comfortably below the real count, so normal file
        # churn won't trip it, but far above zero, so a truncated scan still
        # does.
        assert scanned > 150, (
            f"only {scanned} .html/.py file(s) scanned under {SRC_ROOT}, "
            f"expected well over 150; the scan looks drastically truncated, "
            f"not just missing a file or two"
        )
        return missing

    def test_every_translatable_literal_has_a_msgid(self):
        missing = self._missing()
        assert not missing, (
            f"{len(missing)} translatable string(s) have no msgid and will render "
            f"English under vi. Add them to django.po and recompile django.mo. "
            f"First few: {missing[:5]}"
        )
