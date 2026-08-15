from html.parser import HTMLParser
from pathlib import Path

import pytest
from django.template.loader import render_to_string
from django.test import override_settings
from django.urls import reverse


TEMPLATES = Path(__file__).parents[1] / "templates" / "web"


class _StructureParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.headings = []
        self.anchor_depth = 0
        self.headings_in_anchors = []
        self.roles = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "a":
            self.anchor_depth += 1
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self.headings.append(tag)
            if self.anchor_depth:
                self.headings_in_anchors.append(tag)
        if attrs.get("role"):
            self.roles.append(attrs["role"])

    def handle_endtag(self, tag):
        if tag == "a":
            self.anchor_depth -= 1


def _parse(html):
    parser = _StructureParser()
    parser.feed(html)
    return parser


def test_action_inbox_starts_with_h1_and_fund_link_is_not_a_heading_wrapper():
    source = (TEMPLATES / "staff/action_inbox.html").read_text()

    assert source.index("<h1") < source.index("<h2")
    assert '<a class="fund-chart-link"' not in source
    assert (
        '<a class="button button-secondary" href="{% url \'web:fund-home\' %}">'
        in source
    )


def test_proposal_detail_does_not_skip_from_h1_to_h3():
    source = (TEMPLATES / "staff/proposal_detail.html").read_text()

    assert '<h2>{% trans "Signed snapshot" %}</h2>' in source


def test_fund_form_partials_do_not_inject_page_headings():
    for name in ("staff/_fund_forms.html", "staff/_fund_verify.html"):
        assert "<h1" not in (TEMPLATES / name).read_text()


@override_settings(LANGUAGE_CODE="en")
def test_full_navigation_messages_are_a_focusable_named_status_region():
    # Every mutation is a full page navigation, so the flash region is a named
    # status region that receives focus on load (staff.js) to be announced.
    html = render_to_string(
        "web/staff/shell.html",
        {"messages": ["Saved"], "nav_items": [], "membership": None},
    )
    parsed = _parse(html)

    assert "status" in parsed.roles
    assert 'tabindex="-1"' in html
    assert 'aria-labelledby="messages-heading"' in html
    assert '<h2 id="messages-heading" class="sr-only">Messages</h2>' in html


def test_core_templates_load_i18n_and_mark_user_copy_for_translation():
    expected = {
        "base.html",
        "login.html",
        "staff/_evidence_level.html",
        "staff/gate_devices.html",
        "staff/gate_log.html",
        "staff/gate_queue.html",
        "staff/gate_registrations.html",
    }

    for name in expected:
        source = (TEMPLATES / name).read_text()
        assert "{% load " in source[:150] and "i18n" in source[:150], name
        assert "{% trans " in source or "{% blocktrans" in source, name


@override_settings(DEBUG=False, LANGUAGE_CODE="en")
def test_custom_error_templates_use_pre_auth_shell_and_actionable_navigation(client):
    not_found = client.get("/not-a-real-route/")

    assert not_found.status_code == 404
    assert b'id="error-heading"' in not_found.content
    assert reverse("login").encode() in not_found.content
    for status in (403, 500):
        html = render_to_string(f"{status}.html")
        assert "LamTo" in html
        assert reverse("login") in html
    server_error = render_to_string("500.html")
    assert "may not have been saved" in server_error
    assert "open the record and check before repeating it" in server_error.lower()


@pytest.mark.parametrize(
    ("url_name", "method", "args"),
    [
        ("web:gate-queue", "get", ()),
        ("web:gate-face-photo", "get", (1,)),
        ("web:gate-face-decide", "post", (1,)),
        ("web:gate-plate-decide", "post", (1,)),
        ("web:gate-registrations", "get", ()),
        ("web:gate-devices", "get", ()),
        ("web:gate-log", "get", ()),
    ],
)
def test_anonymous_gate_requests_redirect_to_login(client, url_name, method, args):
    response = getattr(client, method)(reverse(url_name, args=args))

    assert response.status_code == 302
    assert response.url.startswith(f"{reverse('login')}?next=")
