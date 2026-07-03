"""Unit tests for LegalDataManager and CitationParser."""

from __future__ import annotations

from utils import CitationParser, LegalDataManager


class TestLegalDataManager:
    """Test cases for LegalDataManager."""

    def test_initialization(self):
        manager = LegalDataManager()
        stats = manager.stats()
        assert stats["cases"] >= 1
        assert stats["statutes"] >= 1
        assert stats["contracts"] >= 1

    def test_data_loading(self):
        manager = LegalDataManager()
        assert "smith-v-abc-corp-2022" in manager.cases
        case = manager.get_case("smith-v-abc-corp-2022")
        assert case is not None
        assert case["citation"] == "2022 Cal.App.4th 1234"

    def test_search_cases_ranks_by_relevance(self):
        manager = LegalDataManager()
        results = manager.search_cases("delivery timing breach", "CA")
        assert results, "expected at least one CA result"
        scores = [r["relevance_score"] for r in results]
        assert scores == sorted(scores, reverse=True)
        assert all(r["jurisdiction"] == "CA" for r in results)

    def test_get_contract_resolves_alias(self):
        manager = LegalDataManager()
        contract = manager.get_contract("NDA_v1")
        assert contract is not None
        assert contract["id"] == "standard_nda_template"

    def test_get_brief_framework_by_case_type(self):
        manager = LegalDataManager()
        framework = manager.get_brief_framework("contract_breach")
        assert framework is not None
        assert framework["id"] == "summary_judgment"


class TestCitationParser:
    """Test cases for CitationParser."""

    def test_parse_full_citation(self, parser: CitationParser):
        parsed = parser.parse("Smith v. ABC Corp, 2022 Cal.App.4th 1234")
        assert parsed is not None
        assert parsed["case_name"] == "Smith v. ABC Corp"
        assert parsed["volume"] == 2022
        assert parsed["reporter"] == "Cal.App.4th"
        assert parsed["page"] == 1234

    def test_citation_extraction(self, parser: CitationParser):
        text = (
            "See Smith v. ABC Corp, 2022 Cal.App.4th 1234 and also "
            "410 U.S. 113 for further discussion."
        )
        found = parser.extract_citations(text)
        assert "2022 Cal.App.4th 1234" in found
        assert "410 U.S. 113" in found

    def test_citation_normalization_abbreviates(self, parser: CitationParser):
        normalized = parser.normalize("Johnson v. XYZ Industries, 2020 Cal.4th 567")
        assert "Indus." in normalized
        assert "Industries" not in normalized

    def test_validate_valid_citation(self, parser: CitationParser):
        report = parser.validate("Smith v. ABC Corp, 2022 Cal.App.4th 1234")
        assert report["valid"] is True
        assert report["issues"] == []
        assert report["reporter"]["court"] == "California Court of Appeal"

    def test_validate_flags_unknown_reporter(self, parser: CitationParser):
        report = parser.validate("Doe v. Roe, 5 Fake 99")
        assert report["valid"] is False
        assert any("reporter" in issue.lower() for issue in report["issues"])
