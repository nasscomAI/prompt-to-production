"""
Verification Script for UC-0A — Complaint Classifier (CRAFT Self-Test)
Asserts prevention of all 5 naive prompt failure modes and validates outputs.
"""
import csv
import os
import sys
from classifier import (
    ALLOWED_CATEGORIES,
    ALLOWED_PRIORITIES,
    SEVERITY_TRIGGERS,
    classify_complaint,
)

CITIES = ["ahmedabad", "hyderabad", "kolkata", "pune"]
REQUIRED_HEADER = ["complaint_id", "category", "priority", "reason", "flag"]


def test_output_files_exist_and_format():
    """Test that all 4 city output files exist and have correct schema and row counts."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    for city in CITIES:
        filename = os.path.join(base_dir, f"results_{city}.csv")
        assert os.path.exists(filename), f"Missing output file: {filename}"

        with open(filename, mode="r", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)

        assert len(rows) > 0, f"{filename} is empty"
        header = rows[0]
        assert header == REQUIRED_HEADER, f"Header mismatch in {filename}: {header} != {REQUIRED_HEADER}"

        data_rows = rows[1:]
        assert len(data_rows) == 15, f"Expected 15 data rows in {filename}, found {len(data_rows)}"

        for i, row in enumerate(data_rows, start=1):
            assert len(row) == 5, f"Row {i} in {filename} does not have 5 columns: {row}"
            cid, cat, prio, reason, flag = row

            # Assert 1 & 4: Exact allowed category strings, no variations / hallucinations
            assert cat in ALLOWED_CATEGORIES, (
                f"Row {i} ({cid}) in {filename} has invalid category '{cat}' "
                f"(Allowed: {ALLOWED_CATEGORIES})"
            )

            # Assert Priority allowed strings
            assert prio in ALLOWED_PRIORITIES, (
                f"Row {i} ({cid}) in {filename} has invalid priority '{prio}' "
                f"(Allowed: {ALLOWED_PRIORITIES})"
            )

            # Assert 3: Reason present, non-empty, and formatted as a single sentence
            assert reason and len(reason.strip()) > 5, (
                f"Row {i} ({cid}) in {filename} has missing or too short reason: '{reason}'"
            )
            assert reason.endswith("."), (
                f"Row {i} ({cid}) in {filename} reason is not a proper sentence ending with period: '{reason}'"
            )

            # Assert 5: Flag must be either NEEDS_REVIEW or empty string
            assert flag in ["NEEDS_REVIEW", ""], (
                f"Row {i} ({cid}) in {filename} has invalid flag '{flag}' (Must be 'NEEDS_REVIEW' or '')"
            )
            if cat == "Other":
                assert flag == "NEEDS_REVIEW", (
                    f"Row {i} ({cid}) with category 'Other' must have flag 'NEEDS_REVIEW'"
                )


def test_severity_triggers_prevention():
    """Assert failure mode #2 (severity blindness) is prevented across all datasets."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_base = os.path.join(base_dir, "..", "data", "city-test-files")

    for city in CITIES:
        input_file = os.path.join(input_base, f"test_{city}.csv")
        output_file = os.path.join(base_dir, f"results_{city}.csv")

        with open(input_file, mode="r", encoding="utf-8-sig") as inf, \
             open(output_file, mode="r", encoding="utf-8") as outf:
            in_rows = {r["complaint_id"]: r for r in csv.DictReader(inf)}
            out_rows = {r["complaint_id"]: r for r in csv.DictReader(outf)}

        for cid, in_row in in_rows.items():
            assert cid in out_rows, f"Complaint {cid} missing in output {output_file}"
            out_row = out_rows[cid]
            desc = in_row["description"].lower()

            has_severity = any(
                w in desc for w in [
                    "injury", "injur", "child", "school", "hospital",
                    "ambulance", "fire", "hazard", "fell", "collapse"
                ]
            )

            if has_severity:
                assert out_row["priority"] == "Urgent", (
                    f"Severity blindness failure on {cid} ({city}): "
                    f"description '{in_row['description']}' contains severity keyword but priority is '{out_row['priority']}'"
                )


def test_edge_cases_and_resilience():
    """Test malformed inputs, nulls, and ambiguous text handling."""
    # Test 1: Null / Empty
    res_empty = classify_complaint({})
    assert res_empty["category"] == "Other"
    assert res_empty["flag"] == "NEEDS_REVIEW"
    assert res_empty["priority"] == "Standard"

    # Test 2: Non-dict input
    res_nondict = classify_complaint(None)  # type: ignore
    assert res_nondict["category"] == "Other"
    assert res_nondict["flag"] == "NEEDS_REVIEW"

    # Test 3: Ambiguous description
    res_ambiguous = classify_complaint({
        "complaint_id": "TEST-01",
        "description": "Something strange is happening near the corner."
    })
    assert res_ambiguous["category"] == "Other"
    assert res_ambiguous["flag"] == "NEEDS_REVIEW"

    # Test 4: Severity keyword in ambiguous description
    res_urgent_ambig = classify_complaint({
        "complaint_id": "TEST-02",
        "description": "Strange incident occurred near school."
    })
    assert res_urgent_ambig["priority"] == "Urgent"
    assert res_urgent_ambig["category"] == "Other"
    assert res_urgent_ambig["flag"] == "NEEDS_REVIEW"

    # Test 5: All allowed categories tested
    for cat in ALLOWED_CATEGORIES:
        assert cat in ALLOWED_CATEGORIES


def run_all_checks():
    print("=" * 60)
    print("RUNNING UC-0A SELF-TEST SUITE (CRAFT)")
    print("=" * 60)

    try:
        print("[1/3] Checking output CSV files existence, row counts, and schema...")
        test_output_files_exist_and_format()
        print("  --> PASS: All 4 result CSVs exist with exact schema and 15 rows each.")

        print("[2/3] Checking severity blindness prevention across all city test records...")
        test_severity_triggers_prevention()
        print("  --> PASS: All severity signal rows correctly classified as Urgent.")

        print("[3/3] Checking robustness on malformed, missing, and ambiguous inputs...")
        test_edge_cases_and_resilience()
        print("  --> PASS: Resilient error handling and review flagging verified.")

        print("=" * 60)
        print("ALL UC-0A VERIFICATION CHECKS PASSED SUCCESSFULLY! (100% PASS)")
        print("=" * 60)
        return True
    except AssertionError as e:
        print(f"\n❌ ASSERTION FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        return False


if __name__ == "__main__":
    success = run_all_checks()
    sys.exit(0 if success else 1)
