"""
UC-0C app.py — Growth Calculator
Implemented following RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse
import csv
import os
import sys


def load_dataset(input_path: str) -> tuple[list, list]:
    """
    Skill: load_dataset
    Reads CSV, validates columns, reports null count and specific null rows before returning.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input budget CSV file not found: {input_path}")

    records = []
    null_rows = []

    with open(input_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required_cols = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
        if not required_cols.issubset(set(reader.fieldnames or [])):
            raise ValueError(f"CSV missing required columns. Required: {required_cols}")

        for idx, row in enumerate(reader, start=2):
            records.append(row)
            spend = row.get("actual_spend", "").strip()
            if not spend:
                null_rows.append({
                    "line_number": idx,
                    "period": row.get("period"),
                    "ward": row.get("ward"),
                    "category": row.get("category"),
                    "notes": row.get("notes")
                })

    # Pre-computation null audit log
    print(f"=== NULL AUDIT REPORT ===")
    print(f"Total records loaded: {len(records)}")
    print(f"Total null actual_spend rows detected: {len(null_rows)}")
    for nr in null_rows:
        print(f"  - Line {nr['line_number']}: Period {nr['period']} | Ward: {nr['ward']} | Category: {nr['category']} | Reason: {nr['notes']}")
    print(f"=========================\n")

    return records, null_rows


def compute_growth(records: list, ward: str, category: str, growth_type: str) -> list[dict]:
    """
    Skill: compute_growth
    Calculates per-period growth for given ward, category, and growth_type.
    Applies strict parameter enforcement, formula tracking, and null row handling.
    """
    # Rule 1 Enforcement: Refuse all-ward or all-category aggregation
    if not ward or ward.lower() == "all":
        raise ValueError("REFUSAL: All-ward aggregation is strictly prohibited. Specific ward must be specified.")
    if not category or category.lower() == "all":
        raise ValueError("REFUSAL: All-category aggregation is strictly prohibited. Specific category must be specified.")

    # Rule 4 Enforcement: Refuse if growth-type is not specified
    if not growth_type or growth_type.strip() == "":
        raise ValueError("REFUSAL: --growth-type parameter is missing. Must be explicitly specified (e.g. MoM).")
    if growth_type.upper() != "MOM":
        raise ValueError(f"REFUSAL: Unsupported growth type '{growth_type}'. Only 'MoM' is supported.")

    # Filter matching rows
    filtered = [r for r in records if r.get("ward") == ward and r.get("category") == category]
    if not filtered:
        raise ValueError(f"No records found for ward='{ward}' and category='{category}'.")

    # Sort by period
    filtered.sort(key=lambda x: x.get("period", ""))

    output_rows = []
    prev_spend = None

    for r in filtered:
        period = r.get("period")
        budgeted = r.get("budgeted_amount")
        raw_spend = r.get("actual_spend", "").strip()
        notes = r.get("notes", "").strip()

        # Check if current spend is null
        if not raw_spend:
            output_rows.append({
                "period": period,
                "ward": ward,
                "category": category,
                "budgeted_amount": budgeted,
                "actual_spend": "NULL",
                "mom_growth_percent": "NULL",
                "formula": "N/A - Data missing",
                "flag_notes": f"FLAGGED NULL: {notes}" if notes else "FLAGGED NULL"
            })
            prev_spend = None  # Reset previous spend on null
            continue

        curr_spend = float(raw_spend)

        # Compute growth if previous period spend exists
        if prev_spend is None:
            mom_growth_str = "N/A"
            formula_str = "N/A - First Period or Prev NULL"
        else:
            growth_pct = ((curr_spend - prev_spend) / prev_spend) * 100.0
            mom_growth_str = f"{growth_pct:+.1f}%"
            formula_str = "((Actual_Spend_Current - Actual_Spend_Previous) / Actual_Spend_Previous) * 100"

        output_rows.append({
            "period": period,
            "ward": ward,
            "category": category,
            "budgeted_amount": budgeted,
            "actual_spend": f"{curr_spend:.1f}",
            "mom_growth_percent": mom_growth_str,
            "formula": formula_str,
            "flag_notes": notes
        })

        prev_spend = curr_spend

    return output_rows


def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=False, help="Ward name (e.g. 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=False, help="Category (e.g. 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", required=False, help="Growth type (MoM)")
    parser.add_argument("--output", required=True, help="Path to write output CSV")
    args = parser.parse_args()

    records, _ = load_dataset(args.input)

    try:
        growth_table = compute_growth(records, args.ward, args.category, args.growth_type)
    except ValueError as err:
        print(f"\n[ENFORCEMENT ERROR] {err}", file=sys.stderr)
        sys.exit(1)

    fieldnames = ["period", "ward", "category", "budgeted_amount", "actual_spend", "mom_growth_percent", "formula", "flag_notes"]
    with open(args.output, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(growth_table)

    print(f"Done. Growth output written to {args.output}")


if __name__ == "__main__":
    main()
