"""
UC-0C — Number That Looks Right
Implementation of Ward Budget Growth Calculator conforming strictly to RICE enforcement rules.
"""
import argparse
import csv
import os
import sys

def load_dataset(file_path: str):
    """
    Reads budget CSV file, audits missing actual_spend rows,
    and returns dataset rows along with null audit report.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input file not found: {file_path}")

    rows = []
    null_rows = []

    with open(file_path, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):
            raw_spend = row.get("actual_spend", "").strip()
            if raw_spend == "" or raw_spend.lower() == "null" or raw_spend.lower() == "none":
                row["actual_spend_val"] = None
                null_rows.append((i, row))
            else:
                try:
                    row["actual_spend_val"] = float(raw_spend)
                except ValueError:
                    row["actual_spend_val"] = None
                    null_rows.append((i, row))
            rows.append(row)

    return rows, null_rows

def compute_growth(rows: list, ward: str, category: str, growth_type: str) -> list:
    """
    Computes Month-over-Month (MoM) growth for specified ward and category.
    Includes exact formula used and flags null values explicitly.
    """
    if growth_type != "MoM":
        raise ValueError(f"Unsupported growth type '{growth_type}'. Only 'MoM' is supported.")

    filtered_rows = [r for r in rows if r.get("ward") == ward and r.get("category") == category]
    filtered_rows.sort(key=lambda x: x.get("period", ""))

    if not filtered_rows:
        raise ValueError(f"No records found for ward='{ward}' and category='{category}'.")

    results = []
    prev_spend = None

    for r in filtered_rows:
        period = r.get("period")
        curr_spend = r.get("actual_spend_val")
        notes = r.get("notes", "").strip()
        budgeted = r.get("budgeted_amount", "")

        if curr_spend is None:
            mom_str = f"NULL (Flagged: {notes if notes else 'Missing spend data'})"
            formula_str = "N/A - Missing actual_spend"
            spend_str = "NULL"
        else:
            spend_str = f"{curr_spend:.1f}"
            if prev_spend is None:
                mom_str = "N/A (Base Period or Prior NULL)"
                formula_str = "Base period or prior month missing"
            else:
                diff = curr_spend - prev_spend
                growth_pct = (diff / prev_spend) * 100.0
                mom_str = f"{growth_pct:+.1f}%"
                formula_str = f"({curr_spend:.1f} - {prev_spend:.1f}) / {prev_spend:.1f} * 100"

            prev_spend = curr_spend

        results.append({
            "period": period,
            "ward": ward,
            "category": category,
            "budgeted_amount": budgeted,
            "actual_spend": spend_str,
            "mom_growth": mom_str,
            "formula_used": formula_str,
            "notes": notes
        })

    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Ward Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=False, help="Specific ward name")
    parser.add_argument("--category", required=False, help="Specific budget category")
    parser.add_argument("--growth-type", required=False, help="Growth calculation metric (must be MoM)")
    parser.add_argument("--output", required=True, help="Path to save output CSV")
    args = parser.parse_args()

    # RICE Refusal Enforcements
    if not args.ward or args.ward.lower() in ["all", "any", "all-ward"]:
        print("Refusal Error: Aggregating across all wards is prohibited. Please specify a single --ward.")
        sys.exit(1)

    if not args.category or args.category.lower() in ["all", "any", "all-category"]:
        print("Refusal Error: Aggregating across all categories is prohibited. Please specify a single --category.")
        sys.exit(1)

    if not args.growth_type:
        print("Refusal Error: --growth-type not specified. Please specify '--growth-type MoM'.")
        sys.exit(1)

    rows, null_rows = load_dataset(args.input)

    print(f"Dataset Loaded: {len(rows)} rows. Audited {len(null_rows)} deliberate null actual_spend rows.")
    for line_no, nr in null_rows:
        print(f"  • Flagged Line {line_no}: Period={nr.get('period')}, Ward='{nr.get('ward')}', Category='{nr.get('category')}', Reason='{nr.get('notes')}'")

    results = compute_growth(rows, args.ward, args.category, args.growth_type)

    fieldnames = ["period", "ward", "category", "budgeted_amount", "actual_spend", "mom_growth", "formula_used", "notes"]
    try:
        with open(args.output, mode="w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except PermissionError:
        print(f"Error: Permission denied writing to '{args.output}'. Please close the CSV if open in Excel.")
        sys.exit(1)

    print(f"Calculation complete for '{args.ward}' - '{args.category}'. Output saved to {args.output}")

if __name__ == "__main__":
    main()
