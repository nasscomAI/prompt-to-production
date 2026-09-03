"""
UC-0C — Number That Looks Right (Budget Growth Analysis)
Deterministic municipal budget analytics engine built using RICE → agents.md → skills.md → CRAFT workflow.
Calculates per-period growth for a specified ward and category without guessing or unauthorized aggregation.
"""
import argparse
import csv
import os
import sys


ALLOWED_GROWTH_TYPES = ["MoM", "YoY"]

PROHIBITED_AGGREGATION_TERMS = ["all", "all wards", "all categories", "total", "overall", "*"]


def load_dataset(input_path: str) -> tuple:
    """
    Loads the budget dataset, validates schema, and identifies all null actual_spend rows.
    Returns (records, null_records).
    """
    if not os.path.exists(input_path):
        print(f"ERROR: File not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    expected_columns = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
    records = []
    null_records = []

    with open(input_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        header_set = set(reader.fieldnames or [])
        missing = expected_columns - header_set
        if missing:
            print(f"ERROR: Dataset missing required columns: {sorted(list(missing))}", file=sys.stderr)
            sys.exit(1)

        for line_num, row in enumerate(reader, start=2):
            raw_spend = row.get("actual_spend", "").strip()
            parsed_spend = None
            if raw_spend != "":
                try:
                    parsed_spend = float(raw_spend)
                except ValueError:
                    print(f"WARNING: Invalid actual_spend on line {line_num}: {raw_spend}", file=sys.stderr)

            record = {
                "period": row.get("period", "").strip(),
                "ward": row.get("ward", "").strip(),
                "category": row.get("category", "").strip(),
                "budgeted_amount": float(row.get("budgeted_amount", 0.0)),
                "actual_spend": parsed_spend,
                "raw_spend": raw_spend,
                "notes": row.get("notes", "").strip(),
            }
            records.append(record)

            if parsed_spend is None:
                null_records.append(record)

    # Pre-computation reporting of null rows
    print(f"Pre-computation scan found {len(null_records)} rows with null actual_spend:")
    for nr in null_records:
        print(f"  - {nr['period']} | {nr['ward']} | {nr['category']}: {nr['notes']}")

    return records, null_records


def compute_growth(records: list, ward: str, category: str, growth_type: str, output_path: str) -> list:
    """
    Computes per-period growth for the specified ward, category, and growth_type.
    Enforces scope restrictions and outputs results with explicit formulas.
    """
    # 1. Enforce ward and category non-aggregation
    if not ward or ward.strip().lower() in PROHIBITED_AGGREGATION_TERMS:
        print(
            "ERROR: All-ward aggregation is strictly prohibited. "
            "You must specify an individual ward (e.g. --ward 'Ward 1 – Kasba').",
            file=sys.stderr
        )
        sys.exit(1)

    if not category or category.strip().lower() in PROHIBITED_AGGREGATION_TERMS:
        print(
            "ERROR: All-category aggregation is strictly prohibited. "
            "You must specify an individual category (e.g. --category 'Roads & Pothole Repair').",
            file=sys.stderr
        )
        sys.exit(1)

    # 2. Enforce growth type requirement
    if not growth_type:
        print(
            "ERROR: --growth-type must be explicitly specified (e.g. --growth-type MoM). "
            "Growth type cannot be assumed or guessed.",
            file=sys.stderr
        )
        sys.exit(1)

    if growth_type not in ALLOWED_GROWTH_TYPES:
        print(
            f"ERROR: Unsupported growth type '{growth_type}'. "
            f"Supported growth types: {', '.join(ALLOWED_GROWTH_TYPES)}.",
            file=sys.stderr
        )
        sys.exit(1)

    # 3. Filter records strictly by ward and category
    subset = [r for r in records if r["ward"] == ward and r["category"] == category]
    if not subset:
        print(f"ERROR: No matching records for ward '{ward}' and category '{category}'.", file=sys.stderr)
        sys.exit(1)

    # Sort chronologically by period
    subset.sort(key=lambda x: x["period"])

    output_rows = []
    prev_record = None

    for r in subset:
        curr_period = r["period"]
        budgeted = f"{r['budgeted_amount']:.1f}"
        curr_spend = r["actual_spend"]
        notes = r["notes"]

        if curr_spend is None:
            # Deliberate null row — preserve notes and never treat as 0
            actual_spend_str = "NULL"
            growth_pct_str = "NULL"
            formula_str = f"Not computed (null actual_spend: {notes})"
        elif prev_record is None:
            # Baseline period (first period)
            actual_spend_str = f"{curr_spend:.1f}"
            growth_pct_str = "n/a"
            formula_str = "n/a (baseline period: first observation)"
        elif prev_record["actual_spend"] is None:
            # Previous period had null actual spend, cannot compute MoM
            actual_spend_str = f"{curr_spend:.1f}"
            growth_pct_str = "n/a"
            formula_str = f"n/a (previous period {prev_record['period']} actual_spend is null)"
        else:
            prev_spend = prev_record["actual_spend"]
            growth = ((curr_spend - prev_spend) / prev_spend) * 100.0
            sign = "+" if growth > 0 else ""
            growth_pct_str = f"{sign}{growth:.1f}%"
            formula_str = f"(({curr_spend:.1f} - {prev_spend:.1f}) / {prev_spend:.1f}) * 100 = {growth_pct_str}"
            actual_spend_str = f"{curr_spend:.1f}"

        output_rows.append({
            "ward": ward,
            "category": category,
            "period": curr_period,
            "budgeted_amount": budgeted,
            "actual_spend": actual_spend_str,
            "growth_type": growth_type,
            "growth_pct": growth_pct_str,
            "formula": formula_str,
            "notes": notes,
        })

        prev_record = r

    # Write output CSV
    fieldnames = [
        "ward", "category", "period", "budgeted_amount",
        "actual_spend", "growth_type", "growth_pct", "formula", "notes"
    ]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"Generated {len(output_rows)} per-period growth rows for '{ward}' / '{category}'.")
    print(f"Results written to {output_path}")
    return output_rows


def main():
    parser = argparse.ArgumentParser(
        description="UC-0C — Budget Growth Analysis (Number That Looks Right)"
    )
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=False, default=None, help="Target ward name")
    parser.add_argument("--category", required=False, default=None, help="Target budget category")
    parser.add_argument("--growth-type", required=False, default=None, help="Growth type (MoM, YoY)")
    parser.add_argument("--output", required=True, help="Path to output CSV")

    args = parser.parse_args()

    records, null_records = load_dataset(args.input)
    compute_growth(records, args.ward, args.category, args.growth_type, args.output)


if __name__ == "__main__":
    main()
