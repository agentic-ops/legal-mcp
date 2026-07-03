"""Unit tests for clause risk helpers."""

from __future__ import annotations

from tools.risk_helpers import find_missing_clauses


class TestFindMissingClauses:
    def test_nda_missing_expected_topics(self):
        missing = find_missing_clauses(
            ["confidentiality_scope", "term_duration"],
            "NDA",
        )
        assert "return" in missing
        assert "governing_law" in missing
        assert "remed" in missing

    def test_msa_tech_term_topic_matches_variant_key(self):
        missing = find_missing_clauses(
            [
                "scope_of_services",
                "term_and_termination",
                "limitation_of_liability",
                "governing_law",
            ],
            "MSA",
        )
        assert missing == []

    def test_unknown_type_uses_generic_topics(self):
        missing = find_missing_clauses(["governing_law"], None)
        assert "term" in missing
        assert "liab" in missing
        assert "governing_law" not in missing
