"""
UC-0C — Number That Looks Right
Ward Budget Growth Calculator implementation.
"""
import argparse
import csv
import os
import sys


def load_dataset(input_path: str) -> list:
    """
    Reads the CSV budget file and validates columns.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    rows = []
    required_cols = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}

    with open(input_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not required_cols.issubset(set(reader.fieldnames or [])):
            missing = required_cols - set(reader.fieldnames or [])
            raise ValueError(f"Missing required columns in dataset: {missing}")

        for row in reader:
            rows.append(row)

    return rows


def compute_growth(rows: list, ward: str, category: str, growth_type: str) -> list:
    """
    Filters rows by ward and category, calculates growth, and formats outputs.
    """
    # Filter rows matching the specified ward and category exactly
    filtered = [
        row for row in rows 
        if row["ward"].strip().lower() == ward.strip().lower() 
        and row["category"].strip().lower() == category.strip().lower()
    ]

    if not filtered:
        print(f"Warning: No rows matched ward '{ward}' and category '{category}'", file=sys.stderr)

    # Sort chronologically by period
    filtered.sort(key=lambda r: r["period"])

    results = []
    
    for i, row in enumerate(filtered):
        period = row["period"]
        budgeted_amount = row["budgeted_amount"]
        curr_spend_str = row["actual_spend"].strip()
        curr_notes = row["notes"].strip()

        # Check if current spend is null
        is_curr_null = curr_spend_str == ""
        curr_spend = None if is_curr_null else float(curr_spend_str)

        growth = "NULL"
        formula = "N/A"
        notes = curr_notes

        if is_curr_null:
            growth = "NULL"
            formula = "N/A"
            notes = f"[FLAGGED: NULL] {curr_notes}".strip()
        elif i == 0:
            growth = "N/A"
            formula = "N/A"
        else:
            prev_row = filtered[i - 1]
            prev_spend_str = prev_row["actual_spend"].strip()
            is_prev_null = prev_spend_str == ""
            prev_spend = None if is_prev_null else float(prev_spend_str)

            if is_prev_null:
                growth = "NULL"
                formula = "N/A"
                notes = "Cannot compute MoM growth because previous period's spend was null."
            else:
                # Calculate MoM growth
                diff = curr_spend - prev_spend
                pct = (diff / prev_spend) * 100
                
                # Format growth string (e.g. +33.1% or -34.8% or 0.0%)
                if pct > 0:
                    growth = f"+{pct:.1f}%"
                elif pct < 0:
                    growth = f"{pct:.1f}%"
                else:
                    growth = "0.0%"

                formula = f"({curr_spend} - {prev_spend}) / {prev_spend}"

        results.append({
            "period": period,
            "ward": row["ward"],
            "category": row["category"],
            "budgeted_amount": budgeted_amount,
            "actual_spend": curr_spend_str if not is_curr_null else "NULL",
            "growth": growth,
            "formula": formula,
            "notes": notes
        })

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Ward Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to input budget CSV file")
    parser.add_argument("--ward", help="Filter by ward name (exact)")
    parser.add_argument("--category", help="Filter by category name (exact)")
    parser.add_argument("--growth-type", help="MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to output CSV file")
    args = parser.parse_args()

    # Rule 4: If --growth-type not specified — refuse and ask, never guess
    if not args.growth_type:
        print("Refusal: --growth-type must be explicitly specified. Please specify '--growth-type MoM'.", file=sys.stderr)
        sys.exit(1)

    # Rule 1: Never aggregate across wards or categories unless explicitly instructed — refuse if asked
    if not args.ward or not args.category:
        print("Refusal: Calculation across all/multiple wards or categories is not permitted. You must explicitly specify both --ward and --category.", file=sys.stderr)
        sys.exit(1)

    if args.growth_type.upper() != "MOM":
        print(f"Refusal: Growth type '{args.growth_type}' is not supported. YoY is not available due to lack of historical comparative data. Only MoM is supported.", file=sys.stderr)
        sys.exit(1)

    try:
        rows = load_dataset(args.input)
        
        # Rule 2: Flag every null row before computing — report null reason
        # We can report/log the overall nulls in the dataset during loading
        null_rows = [
            r for r in rows if r["actual_spend"].strip() == ""
        ]
        if null_rows:
            print(f"Loaded dataset. Found {len(null_rows)} null actual_spend row(s):", file=sys.stderr)
            for nr in null_rows:
                print(f"  - Period: {nr['period']}, Ward: {nr['ward']}, Category: {nr['category']}. Reason: {nr['notes']}", file=sys.stderr)

        # Compute growth
        results = compute_growth(rows, args.ward, args.category, args.growth_type)

        # Write results
        out_dir = os.path.dirname(args.output)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)

        fieldnames = ["period", "ward", "category", "budgeted_amount", "actual_spend", "growth", "formula", "notes"]
        with open(args.output, mode="w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)

        print(f"Growth calculation completed successfully. Results written to {args.output}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
