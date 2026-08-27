"""
Test script for UC-0C — verifies output against README reference values
and checks all four enforcement rules.
"""
import csv
import subprocess
import sys
import os

PASSED = 0
FAILED = 0

def check(name, condition):
    global PASSED, FAILED
    if condition:
        print(f"[PASSED] {name}")
        PASSED += 1
    else:
        print(f"[FAILED] {name}")
        FAILED += 1


def load_output(path):
    with open(path, 'r', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def test_reference_values():
    """Test against README reference values"""
    print("=" * 60)
    print("TEST 1: Reference Value Verification")
    print("=" * 60)

    rows = load_output("growth_output.csv")

    # Reference: Ward 1 Kasba, Roads, 2024-07 = 19.7 actual, +33.1% MoM
    jul_row = [r for r in rows if r["period"] == "2024-07"][0]
    check("2024-07 actual_spend = 19.7", jul_row["actual_spend"] == "19.7")
    check("2024-07 MoM growth = +33.1%", jul_row["growth_value"] == "+33.1%")

    # Reference: Ward 1 Kasba, Roads, 2024-10 = 13.1, -34.8% MoM
    oct_row = [r for r in rows if r["period"] == "2024-10"][0]
    check("2024-10 actual_spend = 13.1", oct_row["actual_spend"] == "13.1")
    check("2024-10 MoM growth = -34.8%", oct_row["growth_value"] == "-34.8%")


def test_null_flagging():
    """Test enforcement rule: Flag every null row"""
    print("\n" + "=" * 60)
    print("TEST 2: Null Flagging (Ward 4 Warje Roads 2024-07)")
    print("=" * 60)

    # Run for Ward 4 Warje which has a null in 2024-07
    subprocess.run([
        sys.executable, "app.py",
        "--input", "../data/budget/ward_budget.csv",
        "--ward", "Ward 4 \u2013 Warje",
        "--category", "Roads & Pothole Repair",
        "--growth-type", "MoM",
        "--output", "test_null_output.csv"
    ], capture_output=True, text=True)

    rows = load_output("test_null_output.csv")
    jul_row = [r for r in rows if r["period"] == "2024-07"][0]
    check("Null row actual_spend shows 'NULL'", jul_row["actual_spend"] == "NULL")
    check("Null row has NULL_DATA flag", "NULL_DATA" in jul_row["flag"])
    check("Null row formula says N/A", "N/A" in jul_row["formula"])

    # The month AFTER a null should also be flagged as gap
    aug_row = [r for r in rows if r["period"] == "2024-08"][0]
    check("Post-null row flagged as GAP", "GAP" in aug_row.get("flag", "") or "N/A" in aug_row["growth_value"])

    os.remove("test_null_output.csv")


def test_formula_shown():
    """Test enforcement rule: Show formula in every output row"""
    print("\n" + "=" * 60)
    print("TEST 3: Formula Shown in Every Row")
    print("=" * 60)

    rows = load_output("growth_output.csv")
    all_have_formula = all(r["formula"].strip() != "" for r in rows)
    check("Every row has a non-empty formula column", all_have_formula)

    # Check that computed rows show the actual math
    feb_row = [r for r in rows if r["period"] == "2024-02"][0]
    check("Formula contains actual numbers", "12.2" in feb_row["formula"] and "13.3" in feb_row["formula"])


def test_growth_type_refusal():
    """Test enforcement rule: Refuse if growth-type not specified"""
    print("\n" + "=" * 60)
    print("TEST 4: Refusal on Invalid Growth Type")
    print("=" * 60)

    result = subprocess.run([
        sys.executable, "app.py",
        "--input", "../data/budget/ward_budget.csv",
        "--ward", "Ward 1 \u2013 Kasba",
        "--category", "Roads & Pothole Repair",
        "--growth-type", "INVALID",
        "--output", "test_refuse_output.csv"
    ], capture_output=True, text=True)

    check("Script refuses invalid growth-type", result.returncode != 0)
    check("Refusal message mentions 'REFUSED'", "REFUSED" in result.stdout or "REFUSED" in result.stderr)

    if os.path.exists("test_refuse_output.csv"):
        os.remove("test_refuse_output.csv")


def test_no_cross_aggregation():
    """Test enforcement rule: Never aggregate across wards"""
    print("\n" + "=" * 60)
    print("TEST 5: No Cross-Ward Aggregation")
    print("=" * 60)

    rows = load_output("growth_output.csv")
    wards = set(r["ward"] for r in rows)
    check("Output contains exactly one ward", len(wards) == 1)

    categories = set(r["category"] for r in rows)
    check("Output contains exactly one category", len(categories) == 1)


if __name__ == "__main__":
    print("UC-0C Test Suite — Number That Looks Right")
    print("=" * 60)
    print()

    test_reference_values()
    test_null_flagging()
    test_formula_shown()
    test_growth_type_refusal()
    test_no_cross_aggregation()

    print("\n" + "=" * 60)
    print(f"FINAL RESULTS: {PASSED} Passed, {FAILED} Failed")
    if FAILED == 0:
        print("All enforcement rules verified successfully!")
    else:
        print("Some tests failed — review output above.")
    print("=" * 60)
