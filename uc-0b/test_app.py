"""
Tests for app.py — UC-0B Policy Summariser
Covers retrieve_policy and summarize_policy with both happy-path and
error-condition test values.
"""
import os
import sys
import tempfile
import warnings
import pytest

# Allow importing from the same directory
sys.path.insert(0, os.path.dirname(__file__))
from app import (
    retrieve_policy,
    summarize_policy,
    _check_scope_bleed,
    _check_verb_softening,
    _check_clause_coverage,
    MANDATORY_CLAUSES,
)

# ---------------------------------------------------------------------------
# Minimal valid policy text containing all 10 mandatory clauses
# ---------------------------------------------------------------------------
VALID_POLICY = """\
1.1 This policy governs all leave entitlements for permanent employees.

2.3 Employees must submit a leave application at least 14 calendar
    days in advance using Form HR-L1.
2.4 Leave applications must receive written approval from the
    employee's direct manager before the leave commences.
    Verbal approval is not valid.
2.5 Unapproved absence will be recorded as Loss of Pay (LOP)
    regardless of subsequent approval.
2.6 Employees may carry forward a maximum of 5 unused annual leave
    days to the following calendar year. Any days above 5 are
    forfeited on 31 December.
2.7 Carry-forward days must be used within the first quarter
    (January-March) of the following year or they are forfeited.
3.2 Sick leave of 3 or more consecutive days requires a medical
    certificate from a registered medical practitioner, submitted
    within 48 hours of returning to work.
3.4 Sick leave taken immediately before or after a public holiday
    or annual leave period requires a medical certificate regardless
    of duration.
5.2 LWP requires approval from the Department Head and the
    HR Director. Manager approval alone is not sufficient.
5.3 LWP exceeding 30 continuous days requires approval from
    the Municipal Commissioner.
7.2 Leave encashment during service is not permitted under any
    circumstances.
"""


def _write_temp(content: str, suffix: str = ".txt") -> str:
    """Write content to a temp file and return the path."""
    f = tempfile.NamedTemporaryFile(
        mode="w", suffix=suffix, delete=False, encoding="utf-8"
    )
    f.write(content)
    f.close()
    return f.name


# ===========================================================================
# retrieve_policy — happy path
# ===========================================================================

class TestRetrievePolicyHappyPath:
    def test_returns_list_of_dicts(self):
        path = _write_temp(VALID_POLICY)
        sections = retrieve_policy(path)
        os.unlink(path)
        assert isinstance(sections, list)
        assert all(isinstance(s, dict) for s in sections)

    def test_all_10_mandatory_clauses_present(self):
        path = _write_temp(VALID_POLICY)
        sections = retrieve_policy(path)
        os.unlink(path)
        found = {s["clause_number"] for s in sections}
        for clause in MANDATORY_CLAUSES:
            assert clause in found, f"Mandatory clause {clause} missing from parsed sections"

    def test_each_section_has_required_keys(self):
        path = _write_temp(VALID_POLICY)
        sections = retrieve_policy(path)
        os.unlink(path)
        for s in sections:
            assert "clause_number" in s
            assert "heading" in s
            assert "body" in s

    def test_clause_body_verbatim_content(self):
        """Clause 2.5 body must contain the binding verb 'will'."""
        path = _write_temp(VALID_POLICY)
        sections = retrieve_policy(path)
        os.unlink(path)
        clause_25 = next(s for s in sections if s["clause_number"] == "2.5")
        assert "will" in clause_25["body"].lower()

    def test_clause_52_contains_both_approvers(self):
        """Clause 5.2 body must name Department Head AND HR Director."""
        path = _write_temp(VALID_POLICY)
        sections = retrieve_policy(path)
        os.unlink(path)
        clause_52 = next(s for s in sections if s["clause_number"] == "5.2")
        assert "Department Head" in clause_52["body"]
        assert "HR Director" in clause_52["body"]


# ===========================================================================
# retrieve_policy — error handling
# ===========================================================================

class TestRetrievePolicyErrors:
    def test_file_not_found_raises(self):
        with pytest.raises(FileNotFoundError, match="file not found"):
            retrieve_policy("/nonexistent/path/policy.txt")

    def test_non_txt_raises_type_error(self):
        path = _write_temp(VALID_POLICY, suffix=".pdf")
        try:
            with pytest.raises(TypeError, match=".txt"):
                retrieve_policy(path)
        finally:
            os.unlink(path)

    def test_empty_file_raises_value_error(self):
        path = _write_temp("   \n  ")
        try:
            with pytest.raises(ValueError, match="empty"):
                retrieve_policy(path)
        finally:
            os.unlink(path)

    def test_unstructured_file_returns_single_section_with_warning(self):
        path = _write_temp("This policy has no numbered clauses at all.\n")
        try:
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                sections = retrieve_policy(path)
                assert len(sections) == 1
                assert sections[0]["clause_number"] == "UNSTRUCTURED"
                assert any("UNSTRUCTURED" in str(warning.message) for warning in w)
        finally:
            os.unlink(path)


# ===========================================================================
# summarize_policy — happy path
# ===========================================================================

class TestSummarizePolicyHappyPath:
    def _get_sections(self):
        path = _write_temp(VALID_POLICY)
        sections = retrieve_policy(path)
        os.unlink(path)
        return sections

    def test_returns_string(self):
        summary = summarize_policy(self._get_sections())
        assert isinstance(summary, str)
        assert len(summary) > 0

    def test_all_10_clauses_referenced_in_output(self):
        summary = summarize_policy(self._get_sections())
        for clause in MANDATORY_CLAUSES:
            assert clause in summary, f"Clause {clause} missing from summary output"

    def test_clause_52_names_both_approvers(self):
        """The critical multi-condition check: both approvers must appear."""
        summary = summarize_policy(self._get_sections())
        assert "Department Head" in summary
        assert "HR Director" in summary

    def test_clause_24_marks_verbal_invalid(self):
        """Clause 2.4 must state verbal approval is not valid."""
        summary = summarize_policy(self._get_sections())
        assert "Verbal approval is not valid" in summary or "verbal" in summary.lower()

    def test_clause_72_uses_not_permitted(self):
        """Binding verb 'not permitted' must not be softened."""
        summary = summarize_policy(self._get_sections())
        assert "not permitted" in summary.lower()

    def test_clause_25_uses_will(self):
        """Binding verb 'will' in clause 2.5 must not be softened."""
        summary = summarize_policy(self._get_sections())
        # Find the clause 2.5 paragraph
        match = re.search(r"Clause 2\.5:(.*?)(?=Clause \d|\Z)", summary, re.DOTALL | re.IGNORECASE)
        assert match, "Clause 2.5 paragraph not found"
        assert "will" in match.group(1).lower()

    def test_verbatim_flag_on_multi_condition_clauses(self):
        """Clauses 2.4 and 5.2 must carry the VERBATIM flag."""
        summary = summarize_policy(self._get_sections())
        # Find each of the known multi-condition clauses
        for clause in ("2.4", "5.2"):
            pattern = re.compile(
                r"Clause " + re.escape(clause) + r":(.*?)(?=Clause \d|\Z)",
                re.DOTALL | re.IGNORECASE,
            )
            m = pattern.search(summary)
            assert m, f"Clause {clause} paragraph not found"
            assert "VERBATIM" in m.group(1), (
                f"Clause {clause} is multi-condition but lacks VERBATIM flag"
            )


# ===========================================================================
# summarize_policy — error handling
# ===========================================================================

class TestSummarizePolicyErrors:
    def test_empty_sections_raises(self):
        with pytest.raises(ValueError, match="empty"):
            summarize_policy([])

    def test_unstructured_input_raises(self):
        with pytest.raises(ValueError, match="UNSTRUCTURED"):
            summarize_policy([{"clause_number": "UNSTRUCTURED", "heading": "", "body": "text"}])

    def test_missing_mandatory_clause_raises(self):
        """Remove clause 5.2 from source — summarize_policy must halt with ValueError."""
        policy_missing_52 = VALID_POLICY.replace(
            "5.2 LWP requires approval from the Department Head and the\n"
            "    HR Director. Manager approval alone is not sufficient.\n",
            "",
        )
        path = _write_temp(policy_missing_52)
        sections = retrieve_policy(path)
        os.unlink(path)
        with pytest.raises(ValueError, match="5.2"):
            summarize_policy(sections)


# ===========================================================================
# Enforcement helpers — unit tests
# ===========================================================================

class TestScopeBleedCheck:
    def test_removes_scope_bleed_phrase(self):
        text = "Employees must apply. As is standard practice, 14 days notice is needed."
        cleaned = _check_scope_bleed(text)
        assert "as is standard practice" not in cleaned.lower()

    def test_clean_text_unchanged(self):
        text = "Clause 2.3: Employees must submit a leave application 14 days in advance."
        assert _check_scope_bleed(text) == text

    def test_multiple_phrases_all_removed(self):
        text = (
            "Typically in government organisations this applies. "
            "Employees are generally expected to comply."
        )
        cleaned = _check_scope_bleed(text)
        assert "typically in government organisations" not in cleaned.lower()
        assert "employees are generally expected to" not in cleaned.lower()


class TestClauseCoverageCheck:
    def test_detects_missing_clause(self):
        summary = "Clause 2.3: text. Clause 2.4: text. Clause 2.5: text."
        missing = _check_clause_coverage(summary)
        # 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2 should be missing
        assert "2.6" in missing
        assert "5.2" in missing
        assert "7.2" in missing

    def test_no_missing_when_all_present(self):
        summary = " ".join(f"Clause {c}: text." for c in MANDATORY_CLAUSES)
        assert _check_clause_coverage(summary) == []


import re
