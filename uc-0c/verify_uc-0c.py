"""
Verification Script for UC-0C — Number That Looks Right (CRAFT Self-Test)
Asserts prevention of wrong aggregation level, silent null handling, and formula assumptions.
"""
import csv
import os
import sys
from app import load_dataset, compute_growth


def test_growth_output_csv():
    """Verify growth_output.csv exists, schema is correct, and reference values match."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(base_dir, "growth_output.csv")
    assert os.path.exists(output_path), f"Output file missing: {output_path}"

    with open(output_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) == 12, f"Expected 12 monthly rows in output, found {len(rows)}"

    expected_cols = [
        "period", "ward", "category", "budgeted_amount", "actual_spend",
        "growth_type", "growth_rate", "formula", "status", "notes"
    ]
    assert reader.fieldnames == expected_cols, f"Schema mismatch: {reader.fieldnames} != {expected_cols}"

    rows_by_period = {r["period"]: r for r in rows}

    # Reference value check 1: 2024-07 -> +33.1%
    row_jul = rows_by_period.get("2024-07")
    assert row_jul is not None, "Missing 2024-07 row"
    assert row_jul["actual_spend"] == "19.7", f"Expected spend 19.7, got {row_jul['actual_spend']}"
    assert row_jul["growth_rate"] == "+33.1%", f"Expected +33.1%, got {row_jul['growth_rate']}"
    assert "(19.7 - 14.8) / 14.8 * 100" in row_jul["formula"], f"Formula mismatch: {row_jul['formula']}"

    # Reference value check 2: 2024-10 -> -34.8%
    row_oct = rows_by_period.get("2024-10")
    assert row_oct is not None, "Missing 2024-10 row"
    assert row_oct["actual_spend"] == "13.1", f"Expected spend 13.1, got {row_oct['actual_spend']}"
    assert row_oct["growth_rate"] == "-34.8%", f"Expected -34.8%, got {row_oct['growth_rate']}"
    assert "(13.1 - 20.1) / 20.1 * 100" in row_oct["formula"], f"Formula mismatch: {row_oct['formula']}"

    # Formula transparency check: every row has a non-empty formula
    for r in rows:
        assert r["formula"] and len(r["formula"].strip()) > 0, f"Missing formula in period {r['period']}"


def test_null_auditing_and_flagging():
    """Verify all 5 deliberate null rows are detected and properly flagged when computed."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(base_dir, "..", "data", "budget", "ward_budget.csv")
    dataset, null_rows = load_dataset(input_path)

    assert len(dataset) == 300, f"Expected 300 dataset rows, got {len(dataset)}"
    assert len(null_rows) == 5, f"Expected exactly 5 null rows, found {len(null_rows)}"

    expected_null_keys = {
        ("2024-03", "Ward 2 – Shivajinagar", "Drainage & Flooding"),
        ("2024-05", "Ward 5 – Hadapsar", "Streetlight Maintenance"),
        ("2024-07", "Ward 4 – Warje", "Roads & Pothole Repair"),
        ("2024-08", "Ward 3 – Kothrud", "Parks & Greening"),
        ("2024-11", "Ward 1 – Kasba", "Waste Management"),
    }

    actual_null_keys = {(nr["period"], nr["ward"], nr["category"]) for nr in null_rows}
    assert actual_null_keys == expected_null_keys, (
        f"Null row mismatch: {actual_null_keys} != {expected_null_keys}"
    )

    # Test that computing on a dataset containing a null flags the null row rather than skipping/guessing
    shivaji_results = compute_growth(
        dataset,
        ward="Ward 2 – Shivajinagar",
        category="Drainage & Flooding",
        growth_type="MoM",
    )
    march_row = next(r for r in shivaji_results if r["period"] == "2024-03")
    assert march_row["status"] == "FLAGGED_NULL", f"Expected FLAGGED_NULL, got {march_row['status']}"
    assert march_row["growth_rate"] == "NULL (Data Missing)"
    assert "not submitted" in march_row["notes"].lower()


def test_refusal_rules():
    """Verify enforcement refusals for all-ward aggregation, missing growth type, etc."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(base_dir, "..", "data", "budget", "ward_budget.csv")
    dataset, _ = load_dataset(input_path)

    # Refusal 1: All-ward aggregation
    try:
        compute_growth(dataset, ward="All Wards", category="Roads & Pothole Repair", growth_type="MoM")
        assert False, "Should have refused all-ward aggregation"
    except ValueError as e:
        assert "REFUSAL" in str(e) or "prohibited" in str(e).lower()

    # Refusal 2: All-category aggregation
    try:
        compute_growth(dataset, ward="Ward 1 – Kasba", category="*", growth_type="MoM")
        assert False, "Should have refused all-category aggregation"
    except ValueError as e:
        assert "REFUSAL" in str(e) or "prohibited" in str(e).lower()

    # Refusal 3: Missing growth-type
    try:
        compute_growth(dataset, ward="Ward 1 – Kasba", category="Roads & Pothole Repair", growth_type="")
        assert False, "Should have refused missing growth-type"
    except ValueError as e:
        assert "REFUSAL" in str(e) or "prohibited" in str(e).lower()


def run_all_checks():
    print("=" * 60)
    print("RUNNING UC-0C SELF-TEST SUITE (CRAFT)")
    print("=" * 60)

    try:
        print("[1/3] Checking growth_output.csv schema, 12-month series, and reference values (+33.1%, -34.8%)...")
        test_growth_output_csv()
        print("  --> PASS: Reference values match exactly (+33.1% July, -34.8% October) with formula strings.")

        print("[2/3] Checking null detection & flagging across all 5 deliberate null rows...")
        test_null_auditing_and_flagging()
        print("  --> PASS: All 5 deliberate null rows detected and properly flagged with notes.")

        print("[3/3] Checking enforcement refusal rules (all-ward aggregation & unspecified formula)...")
        test_refusal_rules()
        print("  --> PASS: System strictly refuses all-ward wildcards and missing growth types.")

        print("=" * 60)
        print("ALL UC-0C VERIFICATION CHECKS PASSED SUCCESSFULLY! (100% PASS)")
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
