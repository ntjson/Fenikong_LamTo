"""Unit tests for env secret coalescing (empty + whitespace-only → unset)."""

from django.test import SimpleTestCase

from lamto.config.secrets import coalesce_secret


class CoalesceSecretTests(SimpleTestCase):
    def test_empty_and_whitespace_are_unset(self):
        assert coalesce_secret(None) == ""
        assert coalesce_secret("") == ""
        assert coalesce_secret("   ") == ""
        assert coalesce_secret("\t\n") == ""

    def test_empty_and_whitespace_use_default(self):
        default = "0xabc"
        assert coalesce_secret(None, default=default) == default
        assert coalesce_secret("", default=default) == default
        assert coalesce_secret("  \t  ", default=default) == default

    def test_real_key_is_preserved_after_edge_strip(self):
        key = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
        assert coalesce_secret(key) == key
        assert coalesce_secret(f"  {key}  ") == key
