"""
UC-0C Municipal Budget Growth Analyzer
Computes MoM growth per ward per category with null flagging and formula transparency.
"""

import argparse
import csv
import sys

EXPECTED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]


def load_dataset(file_path):
    """Load budget CSV, validate schema, and identify null actual_spend rows."""
    rows = []
    null_rows = []

    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        # Validate schema
        missing_cols = [c for c in EXPECTED_COLUMNS if c not in reader.fieldnames]
        if missing_cols:
            print(f"ERROR: Missing required columns: {missing_cols}", file=sys.stderr)
            sys.exit(1)

        for i, row in enumerate(reader, start=2):
            raw_spend = row.get("actual_spend", "").strip()
            if raw_spend == "" or raw_spend.lower() in ("null", "none"):
                row["actual_spend_val"] = None
                null_rows.append((i, row))
            else:
                row["actual_spend_val"] = float(raw_spend)
            rows.append(row)

    return rows, null_rows


def print_null_audit(null_rows):
    """Print a null value audit report BEFORE any computation."""
    print("=" * 60)
    print("NULL VALUE AUDIT REPORT")
    print("=" * 60)
    print(f"Total null actual_spend rows found: {len(null_rows)}")
    print("-" * 60)

    for row_num, row in null_rows:
        notes = row.get("notes", "").strip()
        print(
            f"  Row {row_num}: {row['period']} | {row['ward']} | {row['category']} "
            f"| Reason: {notes if notes else 'No reason provided'}"
        )

    print("=" * 60)
    print()


def compute_growth(rows, target_ward, target_category, growth_type, output_file):
    """Compute period-over-period growth for a specific ward and category."""
    # Enforcement: refuse missing growth type
    if not growth_type:
        print("ERROR: Refused. --growth-type (e.g. MoM) must be explicitly specified.", file=sys.stderr)
        sys.exit(1)

    # Enforcement: refuse all-ward aggregation
    if target_ward.lower() in ["all", "all wards", "any", "combined"]:
        print("ERROR: Refused. Aggregation across all wards is prohibited. "
              "Please specify a single ward.", file=sys.stderr)
        sys.exit(1)

    filtered = [r for r in rows if r["ward"] == target_ward and r["category"] == target_category]
    filtered.sort(key=lambda x: x["period"])

    if not filtered:
        print(f"ERROR: No data found for ward='{target_ward}', category='{target_category}'.", file=sys.stderr)
        sys.exit(1)

    output_rows = []
    prev_spend = None

    for r in filtered:
        period = r["period"]
        ward = r["ward"]
        category = r["category"]
        budgeted = r["budgeted_amount"]
        curr_spend = r["actual_spend_val"]
        notes = r.get("notes", "").strip()

        if curr_spend is None:
            mom_growth_str = "NULL (Flagged)"
            formula_used = "N/A - actual_spend is NULL"
            status_notes = f"FLAGGED: {notes if notes else 'Missing spend data'}"
            prev_spend = None  # Reset baseline — next valid row becomes new baseline
        else:
            if prev_spend is None:
                mom_growth_str = "N/A (Baseline)"
                formula_used = "N/A - First available period or post-null reset"
                status_notes = notes if notes else "Baseline period"
            else:
                growth_pct = ((curr_spend - prev_spend) / prev_spend) * 100
                mom_growth_str = f"{growth_pct:+.1f}%"
                formula_used = f"(({curr_spend} - {prev_spend}) / {prev_spend}) * 100"
                status_notes = notes if notes else "Computed successfully"
            prev_spend = curr_spend

        output_rows.append({
            "period": period,
            "ward": ward,
            "category": category,
            "budgeted_amount": budgeted,
            "actual_spend": curr_spend if curr_spend is not None else "NULL",
            "mom_growth": mom_growth_str,
            "formula_used": formula_used,
            "status_notes": status_notes
        })

    fieldnames = ["period", "ward", "category", "budgeted_amount", "actual_spend",
                  "mom_growth", "formula_used", "status_notes"]

    with open(output_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"Computed {growth_type} growth for {target_ward} / {target_category}")
    print(f"Output: {len(output_rows)} rows written to {output_file}")


def main():
    parser = argparse.ArgumentParser(description="UC-0C Municipal Budget Growth Analyzer")
    parser.add_argument("--input", required=True, help="Input CSV path")
    parser.add_argument("--ward", required=True, help="Target Ward name")
    parser.add_argument("--category", required=True, help="Target Category name")
    parser.add_argument("--growth-type", required=True, help="Growth calculation type (e.g. MoM)")
    parser.add_argument("--output", required=True, help="Output CSV path")
    args = parser.parse_args()

    # Step 1: Load and audit BEFORE computing
    rows, null_rows = load_dataset(args.input)
    print_null_audit(null_rows)

    # Step 2: Compute growth
    compute_growth(rows, args.ward, args.category, args.growth_type, args.output)


if __name__ == "__main__":
    main()
