"""Shipped CSS and JS carry a content digest in their URL.

Without one, a browser holding a stale ``staff.js`` renders fresh markup
against old handlers: the Compare button is there, its click listener is not,
and clicking it does nothing with no error anywhere.
"""

from pathlib import Path

from django.template import Context, Template
from django.test import SimpleTestCase

from lamto.web.templatetags import assets


def render(path):
    return Template("{% load assets %}{% asset name %}").render(Context({"name": path}))


class AssetVersioningTests(SimpleTestCase):
    def test_shipped_asset_url_carries_a_content_digest(self):
        url = render("web/staff.js")
        self.assertIn("/static/web/staff.js?v=", url)
        digest = url.split("?v=")[1]
        self.assertEqual(len(digest), assets.DIGEST_LENGTH)

    def test_digest_tracks_the_file_contents(self):
        source = Path(assets._absolute_path("web/staff.js"))
        original = source.read_bytes()
        before = render("web/staff.js")
        try:
            source.write_bytes(original + b"\n// touched\n")
            after = render("web/staff.js")
        finally:
            source.write_bytes(original)
        self.assertNotEqual(before, after)
        self.assertEqual(render("web/staff.js"), before)

    def test_distinct_assets_get_distinct_digests(self):
        self.assertNotEqual(
            render("web/staff.js").split("?v=")[1],
            render("web/app.css").split("?v=")[1],
        )

    def test_missing_asset_degrades_to_the_plain_url(self):
        self.assertEqual(render("web/does-not-exist.js"), "/static/web/does-not-exist.js")

    def test_every_shipped_script_and_stylesheet_is_versioned(self):
        import lamto.web

        templates = Path(lamto.web.__file__).parent / "templates"
        offenders = [
            f"{path}:{number}"
            for path in templates.rglob("*.html")
            for number, line in enumerate(path.read_text().splitlines(), start=1)
            if "{% static" in line and (".js'" in line or ".css'" in line)
        ]
        self.assertEqual(offenders, [])
