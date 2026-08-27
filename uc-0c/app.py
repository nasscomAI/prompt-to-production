"""
UC-0C app.py — Number That Looks Right
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
import os
import sys


def load_dataset(input_path):
    """
    Skill: load_dataset
    Reads CSV, validates columns, reports null count and which rows before returning.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    required_columns = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]

    with open(input_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames if reader.fieldnames else []

        # Validate columns
        missing_cols = [col for col in required_columns if col not in headers]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

        rows = list(reader)

    # Report nulls
    null_rows = []
    for i, row in enumerate(rows):
        actual = row.get("actual_spend", "").strip()
        if actual == "":
            null_rows.append({
                "row_index": i + 1,
                "period": row.get("period", ""),
                "ward": row.get("ward", ""),
                "category": row.get("category", ""),
                "reason": row.get("notes", "No reason provided").strip()
            })

    print(f"Loaded {len(rows)} rows from {input_path}")
    print(f"Found {len(null_rows)} null actual_spend values:")
    for nr in null_rows:
        print(f"  - Row {nr['row_index']}: {nr['period']} | {nr['ward']} | {nr['category']} | Reason: {nr['reason']}")

    return rows, null_rows


def compute_growth(rows, ward, category, growth_type, null_rows):
    """
    Skill: compute_growth
    Takes ward + category + growth_type, returns per-period table with formula shown.
    Enforcement:
      - Never aggregate across wards or categories
      - Flag every null row before computing
      - Show formula used in every output row
      - Refuse if growth_type not specified
    """
    # Filter rows for the specified ward and category
    filtered = [r for r in rows if r["ward"] == ward and r["category"] == category]

    if not filtered:
        print(f"ERROR: No data found for ward='{ward}', category='{category}'")
        sys.exit(1)

    # Sort by period
    filtered.sort(key=lambda r: r["period"])

    # Identify null rows in this ward+category combination
    relevant_nulls = [nr for nr in null_rows if nr["ward"] == ward and nr["category"] == category]
    null_periods = set(nr["period"] for nr in relevant_nulls)

    if relevant_nulls:
        print(f"\nWARNING: Null actual_spend found for {ward} / {category}:")
        for nr in relevant_nulls:
            print(f"  - {nr['period']}: {nr['reason']}")

    results = []

    if growth_type == "MoM":
        prev_spend = None
        prev_period = None
        for row in filtered:
            period = row["period"]
            actual_str = row["actual_spend"].strip()
            budgeted = row["budgeted_amount"].strip()

            result_row = {
                "period": period,
                "ward": ward,
                "category": category,
                "budgeted_amount": budgeted,
                "actual_spend": actual_str if actual_str else "NULL",
                "growth_type": "MoM",
                "growth_value": "",
                "formula": "",
                "flag": ""
            }

            if actual_str == "":
                # NULL actual_spend — flag and skip computation
                reason = row.get("notes", "No reason provided").strip()
                result_row["growth_value"] = "NULL"
                result_row["formula"] = "N/A — actual_spend is null"
                result_row["flag"] = f"NULL_DATA: {reason}"
                prev_spend = None  # Break the chain
                prev_period = None
            else:
                current_spend = float(actual_str)

                if prev_spend is None:
                    # First row or after a null — no previous value to compare
                    if prev_period is None and period == filtered[0]["period"]:
                        result_row["growth_value"] = "N/A"
                        result_row["formula"] = "N/A — first period, no prior month"
                    else:
                        result_row["growth_value"] = "N/A"
                        result_row["formula"] = "N/A — prior month is null, cannot compute MoM"
                        result_row["flag"] = "GAP: Prior month data unavailable"
                else:
                    # Compute MoM growth: ((current - previous) / previous) * 100
                    if prev_spend == 0:
                        result_row["growth_value"] = "N/A"
                        result_row["formula"] = "N/A — division by zero (prior month spend = 0)"
                        result_row["flag"] = "DIV_BY_ZERO"
                    else:
                        growth = ((current_spend - prev_spend) / prev_spend) * 100
                        result_row["growth_value"] = f"{growth:+.1f}%"
                        result_row["formula"] = f"(({current_spend} - {prev_spend}) / {prev_spend}) * 100 = {growth:+.1f}%"

                prev_spend = current_spend
                prev_period = period

            results.append(result_row)

    elif growth_type == "YoY":
        # Year-over-Year: compare same month across years
        # With only 2024 data, YoY is not possible
        print("WARNING: Dataset only contains 2024 data. YoY comparison requires multi-year data.")
        for row in filtered:
            period = row["period"]
            actual_str = row["actual_spend"].strip()
            result_row = {
                "period": period,
                "ward": ward,
                "category": category,
                "budgeted_amount": row["budgeted_amount"].strip(),
                "actual_spend": actual_str if actual_str else "NULL",
                "growth_type": "YoY",
                "growth_value": "N/A",
                "formula": "N/A — only single year (2024) data available, cannot compute YoY",
                "flag": "INSUFFICIENT_DATA" if actual_str else f"NULL_DATA: {row.get('notes', '').strip()}"
            }
            results.append(result_row)
    else:
        print(f"ERROR: Unknown growth type '{growth_type}'. Must be 'MoM' or 'YoY'.")
        sys.exit(1)

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name to filter (e.g. 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=True, help="Category to filter (e.g. 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", required=True, dest="growth_type",
                        help="Growth calculation type: MoM or YoY. MUST be specified — system will refuse otherwise.")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    # Enforcement: growth-type is required (argparse handles this, but double-check)
    if args.growth_type not in ("MoM", "YoY"):
        print(f"REFUSED: growth-type must be 'MoM' or 'YoY', got '{args.growth_type}'. Cannot guess.")
        sys.exit(1)

    print(f"=== UC-0C Budget Growth Calculator ===")
    print(f"Ward:        {args.ward}")
    print(f"Category:    {args.category}")
    print(f"Growth Type: {args.growth_type}")
    print(f"Input:       {args.input}")
    print(f"Output:      {args.output}")
    print()

    # Step 1: Load and validate dataset
    rows, null_rows = load_dataset(args.input)

    # Step 2: Compute growth
    results = compute_growth(rows, args.ward, args.category, args.growth_type, null_rows)

    # Step 3: Write output CSV
    output_fields = ["period", "ward", "category", "budgeted_amount", "actual_spend",
                     "growth_type", "growth_value", "formula", "flag"]

    with open(args.output, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=output_fields)
        writer.writeheader()
        writer.writerows(results)

    print(f"\nDone. Growth output written to {args.output}")
    print(f"Total rows: {len(results)}")
    flagged = [r for r in results if r["flag"]]
    if flagged:
        print(f"Flagged rows: {len(flagged)}")
        for fr in flagged:
            print(f"  - {fr['period']}: {fr['flag']}")


if __name__ == "__main__":
    main()
