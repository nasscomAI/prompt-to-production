"""
UC-0C — Number That Looks Right (Granular Ward Budget Growth Engine)
Implementation following RICE -> agents.md -> skills.md -> CRAFT workflow.
"""
import argparse
import csv
import os
from typing import Dict, List, Optional, Tuple, Any

KNOWN_NULL_RECORDS = [
    {"period": "2024-03", "ward": "Ward 2 – Shivajinagar", "category": "Drainage & Flooding"},
    {"period": "2024-07", "ward": "Ward 4 – Warje", "category": "Roads & Pothole Repair"},
    {"period": "2024-11", "ward": "Ward 1 – Kasba", "category": "Waste Management"},
    {"period": "2024-08", "ward": "Ward 3 – Kothrud", "category": "Parks & Greening"},
    {"period": "2024-05", "ward": "Ward 5 – Hadapsar", "category": "Streetlight Maintenance"},
]


def load_dataset(input_path: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Skill 1: load_dataset
    Reads CSV, validates columns, and reports all null/missing actual_spend rows along with notes.
    """
    if not os.path.exists(input_path):
        alt_paths = [
            os.path.join(os.path.dirname(__file__), input_path),
            os.path.join("data", "budget", "ward_budget.csv"),
            os.path.join("..", "data", "budget", "ward_budget.csv"),
        ]
        for p in alt_paths:
            if os.path.exists(p):
                input_path = p
                break
        else:
            raise FileNotFoundError(f"Input budget file not found: {input_path}")

    rows = []
    null_rows = []
    with open(input_path, mode="r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, 1):
            spend_val = row.get("actual_spend", "").strip()
            budget_val = row.get("budgeted_amount", "").strip()

            parsed_budget = float(budget_val) if budget_val else 0.0
            parsed_spend = float(spend_val) if spend_val else None

            row_data = {
                "period": row.get("period", "").strip(),
                "ward": row.get("ward", "").strip(),
                "category": row.get("category", "").strip(),
                "budgeted_amount": parsed_budget,
                "actual_spend": parsed_spend,
                "notes": row.get("notes", "").strip(),
                "line_no": idx,
            }

            if parsed_spend is None:
                null_rows.append(row_data)

            rows.append(row_data)

    return rows, null_rows


def compute_growth(
    rows: List[Dict[str, Any]],
    ward: str,
    category: str,
    growth_type: str,
) -> List[Dict[str, Any]]:
    """
    Skill 2: compute_growth
    Takes ward + category + growth_type, returns granular per-period growth table with explicit formula.
    Enforces:
      - Refusal on all-ward / all-category requests
      - Refusal on missing growth_type
      - Zero silent null handling (flags null with notes)
      - Shows explicit formula on every row
    """
    if not growth_type or growth_type.strip() == "":
        raise ValueError(
            "Refusal: --growth-type is required (e.g. 'MoM' or 'YoY'). "
            "The system refuses to assume or choose a growth formula silently."
        )

    if not ward or ward.lower() in ("all", "all wards", "city", "citywide", "entire city"):
        raise ValueError(
            "Refusal: All-ward aggregation is strictly prohibited by RICE policy. "
            "Please specify an individual ward (e.g. --ward 'Ward 1 – Kasba')."
        )

    if not category or category.lower() in ("all", "all categories"):
        raise ValueError(
            "Refusal: Cross-category aggregation is prohibited. "
            "Please specify an individual category (e.g. --category 'Roads & Pothole Repair')."
        )

    # Filter rows strictly by ward and category
    filtered = [
        r for r in rows
        if r["ward"].strip().lower() == ward.strip().lower()
        and r["category"].strip().lower() == category.strip().lower()
    ]

    if not filtered:
        raise ValueError(f"No records found for ward '{ward}' and category '{category}'.")

    # Sort chronologically by period
    filtered.sort(key=lambda x: x["period"])

    results = []
    prev_spend: Optional[float] = None

    for r in filtered:
        period = r["period"]
        curr_spend = r["actual_spend"]
        budget = r["budgeted_amount"]
        notes = r["notes"]

        if curr_spend is None:
            # Null row flagged before compute
            reason = notes if notes else "Data not reported by ward office"
            results.append({
                "period": period,
                "ward": r["ward"],
                "category": r["category"],
                "budgeted_amount": budget,
                "actual_spend": "NULL",
                "growth_type": growth_type,
                "growth_pct": "N/A (Null Spend)",
                "formula": "Computation halted: actual_spend is NULL",
                "notes": reason,
                "status": "FLAGGED_NULL",
            })
            prev_spend = None
            continue

        if prev_spend is None:
            results.append({
                "period": period,
                "ward": r["ward"],
                "category": r["category"],
                "budgeted_amount": budget,
                "actual_spend": curr_spend,
                "growth_type": growth_type,
                "growth_pct": "N/A (Baseline)",
                "formula": "Baseline period (t0)",
                "notes": notes,
                "status": "COMPUTED",
            })
        else:
            pct_change = ((curr_spend - prev_spend) / prev_spend) * 100
            sign = "+" if pct_change > 0 else ""
            formatted_pct = f"{sign}{pct_change:.1f}%"
            formula_str = f"(({curr_spend} - {prev_spend}) / {prev_spend}) * 100"

            results.append({
                "period": period,
                "ward": r["ward"],
                "category": r["category"],
                "budgeted_amount": budget,
                "actual_spend": curr_spend,
                "growth_type": growth_type,
                "growth_pct": formatted_pct,
                "formula": formula_str,
                "notes": notes,
                "status": "COMPUTED",
            })

        prev_spend = curr_spend

    return results


def run_full_test_suite_and_export_csv(
    test_csv_path: str,
    all_rows: List[Dict[str, Any]],
    null_rows: List[Dict[str, Any]],
):
    """Run comprehensive verification tests and export results to CSV."""
    test_cases = []

    # Test 1: Verify 5 deliberate nulls are discovered
    t1_pass = len(null_rows) == 5
    test_cases.append({
        "test_id": 1,
        "test_name": "Null Spend Detection",
        "description": "Verify that all 5 deliberate null rows are discovered and flagged with notes",
        "expected": "5 null rows with notes",
        "actual": f"{len(null_rows)} null rows detected",
        "status": "PASS" if t1_pass else "FAIL",
    })

    # Test 2: Verify Ward 1 Kasba Roads July 2024 MoM growth (+33.1%)
    w1_roads = compute_growth(all_rows, "Ward 1 – Kasba", "Roads & Pothole Repair", "MoM")
    july_row = next((r for r in w1_roads if r["period"] == "2024-07"), None)
    t2_pass = july_row and july_row["growth_pct"] == "+33.1%"
    test_cases.append({
        "test_id": 2,
        "test_name": "Monsoon Spike Calculation (Ward 1 July)",
        "description": "Verify Ward 1 Kasba Roads July 2024 MoM growth matches reference value (+33.1%)",
        "expected": "+33.1%",
        "actual": july_row["growth_pct"] if july_row else "Not found",
        "status": "PASS" if t2_pass else "FAIL",
    })

    # Test 3: Verify Ward 1 Kasba Roads October 2024 MoM growth (-34.8%)
    oct_row = next((r for r in w1_roads if r["period"] == "2024-10"), None)
    t3_pass = oct_row and oct_row["growth_pct"] == "-34.8%"
    test_cases.append({
        "test_id": 3,
        "test_name": "Post-Monsoon Drop Calculation (Ward 1 Oct)",
        "description": "Verify Ward 1 Kasba Roads Oct 2024 MoM growth matches reference value (-34.8%)",
        "expected": "-34.8%",
        "actual": oct_row["growth_pct"] if oct_row else "Not found",
        "status": "PASS" if t3_pass else "FAIL",
    })

    # Test 4: Verify Ward 2 Shivajinagar Drainage March 2024 is FLAGGED_NULL
    w2_drain = compute_growth(all_rows, "Ward 2 – Shivajinagar", "Drainage & Flooding", "MoM")
    mar_row = next((r for r in w2_drain if r["period"] == "2024-03"), None)
    t4_pass = mar_row and mar_row["status"] == "FLAGGED_NULL"
    test_cases.append({
        "test_id": 4,
        "test_name": "Ward 2 March Null Handling",
        "description": "Verify Ward 2 Shivajinagar Drainage March 2024 is flagged as NULL with note reason",
        "expected": "FLAGGED_NULL",
        "actual": mar_row["status"] if mar_row else "Not found",
        "status": "PASS" if t4_pass else "FAIL",
    })

    # Test 5: Verify Ward 4 Warje Roads July 2024 is FLAGGED_NULL
    w4_roads = compute_growth(all_rows, "Ward 4 – Warje", "Roads & Pothole Repair", "MoM")
    w4_july = next((r for r in w4_roads if r["period"] == "2024-07"), None)
    t5_pass = w4_july and w4_july["status"] == "FLAGGED_NULL"
    test_cases.append({
        "test_id": 5,
        "test_name": "Ward 4 July Null Handling",
        "description": "Verify Ward 4 Warje Roads July 2024 is flagged as NULL rather than computed",
        "expected": "FLAGGED_NULL",
        "actual": w4_july["status"] if w4_july else "Not found",
        "status": "PASS" if t5_pass else "FAIL",
    })

    # Test 6: Verify All-Ward Aggregation Refusal
    t6_pass = False
    try:
        compute_growth(all_rows, "all", "Roads & Pothole Repair", "MoM")
    except ValueError as e:
        if "prohibited" in str(e).lower() or "refusal" in str(e).lower():
            t6_pass = True
    test_cases.append({
        "test_id": 6,
        "test_name": "All-Ward Aggregation Refusal",
        "description": "Verify system strictly refuses cross-ward / city-wide aggregation requests",
        "expected": "Refusal / Exception raised",
        "actual": "Refused with clear policy error" if t6_pass else "Allowed aggregation",
        "status": "PASS" if t6_pass else "FAIL",
    })

    # Test 7: Verify Missing Growth Type Refusal
    t7_pass = False
    try:
        compute_growth(all_rows, "Ward 1 – Kasba", "Roads & Pothole Repair", "")
    except ValueError as e:
        if "growth-type is required" in str(e).lower() or "refusal" in str(e).lower():
            t7_pass = True
    test_cases.append({
        "test_id": 7,
        "test_name": "Formula Assumption Refusal",
        "description": "Verify system refuses to guess formula when --growth-type is omitted",
        "expected": "Refusal / Exception raised",
        "actual": "Refused with clarification prompt" if t7_pass else "Silently assumed formula",
        "status": "PASS" if t7_pass else "FAIL",
    })

    out_dir = os.path.dirname(test_csv_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    fieldnames = ["test_id", "test_name", "description", "expected", "actual", "status"]
    with open(test_csv_path, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(test_cases)

    print(f"Test verification results exported to {test_csv_path}")


def main():
    parser = argparse.ArgumentParser(description="UC-0C Granular Ward Budget Growth Engine")
    parser.add_argument(
        "--input",
        default="../data/budget/ward_budget.csv",
        help="Path to ward_budget.csv",
    )
    parser.add_argument(
        "--ward",
        default="Ward 1 – Kasba",
        help="Specific ward name (aggregation across wards is prohibited)",
    )
    parser.add_argument(
        "--category",
        default="Roads & Pothole Repair",
        help="Specific category name",
    )
    parser.add_argument(
        "--growth-type",
        default="MoM",
        help="Growth formula type: MoM (Month-over-Month) or YoY (Year-over-Year)",
    )
    parser.add_argument(
        "--output",
        default="growth_output.csv",
        help="Path to write per-period growth output CSV",
    )
    parser.add_argument(
        "--test-csv",
        default="results.csv",
        help="Path to write test verification results CSV",
    )
    args = parser.parse_args()

    # Step 1: Load dataset and check nulls
    rows, null_rows = load_dataset(args.input)
    print(f"Loaded {len(rows)} records. Found {len(null_rows)} deliberate null spend rows.")

    # Step 2: Compute granular growth table
    growth_results = compute_growth(rows, args.ward, args.category, args.growth_type)

    # Step 3: Write output CSV
    out_dir = os.path.dirname(args.output)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    fieldnames = [
        "period",
        "ward",
        "category",
        "budgeted_amount",
        "actual_spend",
        "growth_type",
        "growth_pct",
        "formula",
        "notes",
        "status",
    ]
    with open(args.output, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(growth_results)

    print(f"Granular growth output written to {args.output}")

    # Step 4: Run full test suite and export test verification CSV
    run_full_test_suite_and_export_csv(args.test_csv, rows, null_rows)


if __name__ == "__main__":
    main()
