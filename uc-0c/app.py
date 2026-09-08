"""
UC-0C — Number That Looks Right
Budget Growth Calculator built using RICE + agents.md + skills.md + CRAFT framework.
"""
import argparse
import csv
import os
import sys
from typing import Dict, List, Any, Optional, Tuple

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]

def load_dataset(file_path: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Skill: load_dataset
    Reads the budget CSV file, validates columns, audits missing/null actual_spend rows,
    and returns parsed records alongside the list of flagged null rows.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input file not found: {file_path}")

    records: List[Dict[str, Any]] = []
    null_rows: List[Dict[str, Any]] = []

    with open(file_path, mode="r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        
        # Validate columns
        if not reader.fieldnames:
            raise ValueError(f"CSV file is empty: {file_path}")
        
        missing_cols = [col for col in REQUIRED_COLUMNS if col not in reader.fieldnames]
        if missing_cols:
            raise ValueError(f"CSV missing required columns: {missing_cols}")

        for idx, row in enumerate(reader, start=2): # 1-based line number including header
            period = str(row.get("period", "")).strip()
            ward = str(row.get("ward", "")).strip()
            category = str(row.get("category", "")).strip()
            budget_raw = str(row.get("budgeted_amount", "")).strip()
            actual_raw = str(row.get("actual_spend", "")).strip()
            notes = str(row.get("notes", "")).strip()

            budget_val = float(budget_raw) if budget_raw else None
            actual_val = float(actual_raw) if actual_raw else None

            record = {
                "line_num": idx,
                "period": period,
                "ward": ward,
                "category": category,
                "budgeted_amount": budget_val,
                "actual_spend": actual_val,
                "notes": notes
            }
            records.append(record)

            if actual_val is None:
                null_rows.append(record)

    return records, null_rows


def compute_growth(
    records: List[Dict[str, Any]],
    ward: str,
    category: str,
    growth_type: str
) -> List[Dict[str, Any]]:
    """
    Skill: compute_growth
    Takes ward + category + growth_type, filters isolated series, and returns
    a per-period table with explicit formula tracking and safe null handling.
    """
    # 1. Enforcement Rule: Refuse all-ward or multi-ward aggregation
    if not ward or ward.strip().lower() in ["all", "any", "total", "combined", "all wards", "*"]:
        raise PermissionError(
            "REFUSAL: All-ward aggregation is strictly prohibited. "
            "Financial growth must be computed for a specific, isolated ward."
        )

    if not category or category.strip().lower() in ["all", "any", "total", "combined", "all categories", "*"]:
        raise PermissionError(
            "REFUSAL: Cross-category aggregation is strictly prohibited. "
            "Financial growth must be computed for a specific, isolated category."
        )

    # 2. Enforcement Rule: Validate Growth Type
    if not growth_type:
        raise ValueError(
            "REFUSAL: Growth type not specified. "
            "Please explicitly specify --growth-type (e.g., 'MoM' for Month-over-Month)."
        )

    growth_type_upper = growth_type.strip().upper()
    if growth_type_upper not in ["MOM", "YOY"]:
        raise ValueError(
            f"REFUSAL: Unsupported growth type '{growth_type}'. "
            "Allowed values are 'MoM' (Month-over-Month) or 'YoY' (Year-over-Year)."
        )

    # Filter records for the specified ward and category
    filtered = [
        r for r in records
        if r["ward"].strip().lower() == ward.strip().lower()
        and r["category"].strip().lower() == category.strip().lower()
    ]

    if not filtered:
        raise ValueError(f"No records found matching ward='{ward}' and category='{category}'")

    # Sort sequentially by period
    filtered.sort(key=lambda x: x["period"])

    output_table: List[Dict[str, Any]] = []

    for i, current in enumerate(filtered):
        period = current["period"]
        actual_t = current["actual_spend"]
        budget_t = current["budgeted_amount"]
        notes_t = current["notes"]

        if i == 0:
            growth_rate_str = "N/A"
            formula_str = "Base period (no prior period for comparison)"
            status = "Base Period"
            if actual_t is None:
                status = f"NULL: {notes_t}"
        else:
            prev = filtered[i - 1]
            actual_prev = prev["actual_spend"]
            period_prev = prev["period"]
            notes_prev = prev["notes"]

            if actual_t is None:
                growth_rate_str = "NULL"
                formula_str = f"Cannot compute: current period ({period}) actual_spend is NULL"
                status = f"NULL: {notes_t}"
            elif actual_prev is None:
                growth_rate_str = "NULL"
                formula_str = f"Cannot compute: prior period ({period_prev}) actual_spend is NULL"
                status = f"Prior period ({period_prev}) missing: {notes_prev}"
            else:
                growth_val = ((actual_t - actual_prev) / actual_prev) * 100
                growth_rate_str = f"{growth_val:+.1f}%"
                formula_str = f"(({actual_t:.1f} - {actual_prev:.1f}) / {actual_prev:.1f}) * 100 = {growth_val:+.1f}%"
                status = "Computed"

        output_table.append({
            "period": period,
            "ward": current["ward"],
            "category": current["category"],
            "budgeted_amount": f"{budget_t:.1f}" if budget_t is not None else "NULL",
            "actual_spend": f"{actual_t:.1f}" if actual_t is not None else "NULL",
            "growth_type": growth_type_upper,
            "growth_rate": growth_rate_str,
            "formula_used": formula_str,
            "notes": notes_t if notes_t else status
        })

    return output_table


def main():
    parser = argparse.ArgumentParser(
        description="UC-0C — Per-Ward Per-Category Budget Growth Calculator",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--input", default="../data/budget/ward_budget.csv", help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Specific ward name (e.g., 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=True, help="Specific category name (e.g., 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", dest="growth_type", required=False, help="Growth type: 'MoM' or 'YoY'")
    parser.add_argument("--output", default="growth_output.csv", help="Path to write output CSV")

    args = parser.parse_args()

    # Pre-check growth-type presence (Enforcement rule 4)
    if not args.growth_type:
        print("\n[ERROR / REFUSAL]: --growth-type was not provided.")
        print("Enforcement Rule: System refuses to guess between MoM and YoY.")
        print("Please rerun with --growth-type MoM (or --growth-type YoY).\n")
        sys.exit(1)

    try:
        # 1. Load dataset & audit nulls
        records, null_rows = load_dataset(args.input)
        
        print("\n" + "=" * 75)
        print("DATASET AUDIT REPORT: DELIBERATE NULL ROWS DETECTED")
        print("=" * 75)
        print(f"Total Rows: {len(records)} | Total Null actual_spend Rows: {len(null_rows)}")
        for idx, nr in enumerate(null_rows, start=1):
            print(f"  [{idx}] Period: {nr['period']} | Ward: {nr['ward']} | Category: {nr['category']}")
            print(f"      Notes / Null Reason: '{nr['notes']}'")
        print("=" * 75 + "\n")

        # 2. Compute isolated growth
        results = compute_growth(records, args.ward, args.category, args.growth_type)

        # 3. Display output table to console
        print("=" * 75)
        print(f"BUDGET GROWTH TABLE: {args.ward} | {args.category} | {args.growth_type.upper()}")
        print("=" * 75)
        print(f"{'Period':<10} | {'Budget':<8} | {'Actual':<8} | {'Growth':<10} | {'Formula / Reason'}")
        print("-" * 75)
        for r in results:
            print(f"{r['period']:<10} | {r['budgeted_amount']:<8} | {r['actual_spend']:<8} | {r['growth_rate']:<10} | {r['formula_used']}")
        print("=" * 75 + "\n")

        # 4. Save CSV Output
        os.makedirs(os.path.dirname(os.path.abspath(args.output)) if os.path.dirname(args.output) else ".", exist_ok=True)
        fieldnames = ["period", "ward", "category", "budgeted_amount", "actual_spend", "growth_type", "growth_rate", "formula_used", "notes"]
        with open(args.output, mode="w", newline="", encoding="utf-8") as out_f:
            writer = csv.DictWriter(out_f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)

        print(f"Output successfully written to: {args.output}\n")

    except PermissionError as pe:
        print(f"\n[REFUSAL]: {pe}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR]: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
