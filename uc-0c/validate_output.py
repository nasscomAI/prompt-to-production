"""
Result validator for UC-0C output.
Checks the growth_output.csv against reference values from README.md.
"""
import sys

import pandas as pd

REFERENCE_CHECKS = [
    {
        "label": "Kasba Roads Jul 2024 spend",
        "ward": "Ward 1 – Kasba",
        "category": "Roads & Pothole Repair",
        "period": "2024-07",
        "column": "actual_spend",
        "expected": "19.7",
    },
    {
        "label": "Kasba Roads Jul 2024 MoM",
        "ward": "Ward 1 – Kasba",
        "category": "Roads & Pothole Repair",
        "period": "2024-07",
        "column": "growth_rate",
        "expected": "+33.1%",
    },
    {
        "label": "Kasba Roads Oct 2024 spend",
        "ward": "Ward 1 – Kasba",
        "category": "Roads & Pothole Repair",
        "period": "2024-10",
        "column": "actual_spend",
        "expected": "13.1",
    },
    {
        "label": "Kasba Roads Oct 2024 MoM",
        "ward": "Ward 1 – Kasba",
        "category": "Roads & Pothole Repair",
        "period": "2024-10",
        "column": "growth_rate",
        "expected": "-34.8%",
    },
]

NULL_ROW_CHECKS = [
    {
        "label": "Shivajinagar Drainage Mar 2024 null",
        "ward": "Ward 2 – Shivajinagar",
        "category": "Drainage & Flooding",
        "period": "2024-03",
        "expected_flag": "True",
        "expected_reason": "Data not submitted by ward office",
    },
    {
        "label": "Warje Roads Jul 2024 null",
        "ward": "Ward 4 – Warje",
        "category": "Roads & Pothole Repair",
        "period": "2024-07",
        "expected_flag": "True",
        "expected_reason": "Audit freeze — figures under review",
    },
]

AGGREGATION_CHECK_WARDS = ["Ward 1 – Kasba", "Ward 2 – Shivajinagar", "Ward 3 – Kothrud",
                           "Ward 4 – Warje", "Ward 5 – Hadapsar"]


def validate(path: str) -> int:
    df = pd.read_csv(path, keep_default_na=False)
    errors = 0
    total_checks = 0

    REQUIRED_OUTPUT_COLS = {"period", "ward", "category", "actual_spend", "growth_rate", "formula", "null_flag", "null_reason"}
    missing = REQUIRED_OUTPUT_COLS - set(df.columns)
    if missing:
        print(f"FAIL: Missing output columns: {sorted(missing)}")
        return 1

    print(f"Output has {len(df)} rows.")

    for check in REFERENCE_CHECKS:
        total_checks += 1
        row = df[(df["ward"] == check["ward"]) & (df["category"] == check["category"]) & (df["period"] == check["period"])]
        if row.empty:
            print(f"SKIP [{check['label']}]: Not in current subset")
            continue
        val = row.iloc[0][check["column"]]
        if str(val).strip() != check["expected"]:
            print(f"FAIL [{check['label']}]: Expected '{check['expected']}', got '{val}'")
            errors += 1
        else:
            print(f"PASS [{check['label']}]: {val}")

    for check in NULL_ROW_CHECKS:
        total_checks += 1
        row = df[(df["ward"] == check["ward"]) & (df["category"] == check["category"]) & (df["period"] == check["period"])]
        if row.empty:
            print(f"SKIP [{check['label']}]: Not in current subset")
            continue
        flag = str(row.iloc[0]["null_flag"]).strip()
        reason = str(row.iloc[0]["null_reason"]).strip()
        if flag != check["expected_flag"]:
            print(f"FAIL [{check['label']}]: Expected null_flag '{check['expected_flag']}', got '{flag}'")
            errors += 1
        elif reason != check["expected_reason"]:
            print(f"FAIL [{check['label']}]: Expected reason '{check['expected_reason']}', got '{reason}'")
            errors += 1
        else:
            print(f"PASS [{check['label']}]: flag={flag}, reason={reason}")
        gval = str(row.iloc[0]["growth_rate"]).strip()
        if gval != "":
            print(f"FAIL [{check['label']}]: growth_rate should be empty for null row, got '{gval}'")
            errors += 1

    total_checks += 1
    first_row = df.iloc[0]
    if str(first_row["growth_rate"]).strip() != "N/A":
        print(f"FAIL [First period]: First row growth_rate should be 'N/A', got '{first_row['growth_rate']}'")
        errors += 1
    else:
        print(f"PASS [First period]: growth_rate = N/A")

    unique_wards = df["ward"].nunique()
    unique_cats = df["category"].nunique()
    if unique_wards != 1:
        print(f"FAIL [Aggregation]: Expected exactly 1 ward in output, got {unique_wards}")
        errors += 1
    else:
        print(f"PASS [Aggregation]: Single ward output")
    if unique_cats != 1:
        print(f"FAIL [Aggregation]: Expected exactly 1 category in output, got {unique_cats}")
        errors += 1
    else:
        print(f"PASS [Aggregation]: Single category output")

    formula_col = df["formula"].astype(str)
    has_formula = (formula_col != "") & (formula_col != "nan") & (formula_col != "No previous period")
    has_formula_count = has_formula.sum()
    if has_formula_count > 0:
        print(f"PASS [Formula present]: {has_formula_count} rows have formulas")
    else:
        print(f"FAIL [Formula present]: No rows have formulas shown")
        errors += 1

    null_rows = df[df["null_flag"] == "True"]
    if len(null_rows) > 0:
        print(f"INFO [{len(null_rows)} null rows found]")
    else:
        print(f"WARN: No null rows flagged — may be correct for this subset")

    if errors == 0:
        print(f"\nAll applicable checks PASSED.")
    else:
        print(f"\n{errors} check(s) FAILED.")

    return 0 if errors == 0 else 1


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "growth_output.csv"
    sys.exit(validate(path))
