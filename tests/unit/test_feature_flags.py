"""Unit tests for category-level feature flags."""

from __future__ import annotations

from feature_flags import TOOL_CATEGORIES, enabled_categories, is_category_enabled


class TestFeatureFlags:
    def test_all_categories_enabled_by_default(self, monkeypatch):
        for env_name in TOOL_CATEGORIES.values():
            monkeypatch.delenv(env_name, raising=False)
        assert is_category_enabled("research") is True
        assert is_category_enabled("analysis_queue") is True
        categories = enabled_categories()
        assert set(categories) == set(TOOL_CATEGORIES)
        assert all(categories.values())

    def test_explicit_false_disables_category(self, monkeypatch):
        monkeypatch.setenv("LEGAL_MCP_ENABLE_PRIVILEGE", "false")
        assert is_category_enabled("privilege") is False
        assert is_category_enabled("research") is True

    def test_truthy_values_enable_category(self, monkeypatch):
        monkeypatch.setenv("LEGAL_MCP_ENABLE_BRIEF", "yes")
        assert is_category_enabled("brief") is True
