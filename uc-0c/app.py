"""
UC-0C app.py — Ward Budget Growth Calculator.
Implements load_dataset and compute_growth skills with RICE enforcement rules.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
import os
import sys

REQUIRED_COLUMNS = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
VALID_GROWTH_TYPES = {"MoM", "YoY"}


def load_dataset(file_path: str) -> list:
    """
    Skill load_dataset: reads the input budget CSV, validates columns,
    identifies and reports null actual_spend rows, returns all rows.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input file not found: {file_path}")

    with open(file_path, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError("Input CSV file is empty or has no headers.")

        actual_cols = {c.strip() for c in reader.fieldnames}
        missing_cols = REQUIRED_COLUMNS - actual_cols
        if missing_cols:
            raise ValueError(f"Input CSV is missing required columns: {', '.join(sorted(missing_cols))}")

        rows = [row for row in reader]

    if not rows:
        raise ValueError("Input CSV file has no data rows.")

    # Flag every null row upfront (enforcement rule 2)
    null_rows = [r for r in rows if not r["actual_spend"].strip()]
    if null_rows:
        print("=== NULL ROWS DETECTED (will not be computed) ===")
        for r in null_rows:
            reason = r["notes"].strip() if r["notes"].strip() else "No reason provided"
            print(f"  [{r['period']}] {r['ward']} / {r['category']}: NULL — Reason: {reason}")
        print()

    return rows


def compute_growth(dataset: list, ward: str, category: str, growth_type: str) -> list:
    """
    Skill compute_growth: filters dataset by ward+category, computes growth
    showing formula per row, flags null periods without computing.
    """
    # Enforcement rule 4: refuse if growth_type is missing
    if not growth_type:
        raise ValueError("--growth-type is required. Never assumed. Specify 'MoM' or 'YoY'.")
    if growth_type not in VALID_GROWTH_TYPES:
        raise ValueError(f"Invalid --growth-type '{growth_type}'. Must be one of: {', '.join(sorted(VALID_GROWTH_TYPES))}.")

    # Enforcement rule 1: refuse if ward or category looks like an all-ward aggregation
    if not ward or ward.strip().lower() in ("all", "*", ""):
        raise ValueError("All-ward aggregation is not permitted. Specify an exact ward name.")
    if not category or category.strip().lower() in ("all", "*", ""):
        raise ValueError("All-category aggregation is not permitted. Specify an exact category name.")

    # Filter dataset to the requested ward + category
    filtered = [
        r for r in dataset
        if r["ward"].strip() == ward.strip() and r["category"].strip() == category.strip()
    ]

    if not filtered:
        raise ValueError(
            f"No data found for ward='{ward}' and category='{category}'. "
            f"Check exact spelling including dashes and special characters."
        )

    # Sort by period (YYYY-MM) for sequential computation
    filtered = sorted(filtered, key=lambda r: r["period"].strip())

    results = []
    for i, row in enumerate(filtered):
        period = row["period"].strip()
        raw_spend = row["actual_spend"].strip()
        note = row["notes"].strip()

        if not raw_spend:
            # Enforcement rule 2: flag null rows, do not compute
            reason = note if note else "No reason provided"
            results.append({
                "ward": ward,
                "category": category,
                "period": period,
                "actual_spend": "NULL",
                "growth_rate": "N/A",
                "formula": "N/A",
                "flag": f"NULL — {reason}",
            })
            continue

        current_spend = float(raw_spend)

        if growth_type == "MoM":
            if i == 0:
                results.append({
                    "ward": ward,
                    "category": category,
                    "period": period,
                    "actual_spend": f"{current_spend:.1f}",
                    "growth_rate": "N/A (first period)",
                    "formula": "No previous period",
                    "flag": "",
                })
                continue

            # Walk back to find previous non-null period
            prev_row = None
            for j in range(i - 1, -1, -1):
                if filtered[j]["actual_spend"].strip():
                    prev_row = filtered[j]
                    break

            if prev_row is None:
                results.append({
                    "ward": ward,
                    "category": category,
                    "period": period,
                    "actual_spend": f"{current_spend:.1f}",
                    "growth_rate": "N/A",
                    "formula": "No valid previous period",
                    "flag": "",
                })
                continue

            prev_spend = float(prev_row["actual_spend"].strip())
            prev_period = prev_row["period"].strip()
            growth = (current_spend - prev_spend) / prev_spend * 100
            formula_str = f"({current_spend} - {prev_spend}) / {prev_spend} * 100"

            results.append({
                "ward": ward,
                "category": category,
                "period": period,
                "actual_spend": f"{current_spend:.1f}",
                "growth_rate": f"{growth:+.1f}%",
                "formula": formula_str,
                "flag": f"Note: prev period used = {prev_period}" if prev_period != filtered[i - 1]["period"].strip() else "",
            })

        elif growth_type == "YoY":
            # For YoY: compare same month prior year (not in this dataset since only 2024)
            results.append({
                "ward": ward,
                "category": category,
                "period": period,
                "actual_spend": f"{current_spend:.1f}",
                "growth_rate": "N/A (YoY requires multi-year data)",
                "formula": "No prior year data in dataset",
                "flag": "",
            })

    return results


def write_output(growth_table: list, output_path: str):
    """Writes the growth table to a CSV file."""
    if not growth_table:
        raise ValueError("No results to write.")

    fieldnames = ["ward", "category", "period", "actual_spend", "growth_rate", "formula", "flag"]
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    with open(output_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(growth_table)


def main():
    parser = argparse.ArgumentParser(
        description="UC-0C Ward Budget Growth Calculator"
    )
    parser.add_argument("--input",       required=True,  help="Path to ward_budget.csv")
    parser.add_argument("--ward",        required=True,  help="Exact ward name (e.g. 'Ward 1 – Kasba')")
    parser.add_argument("--category",    required=True,  help="Exact category name (e.g. 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", required=True,  dest="growth_type", help="Growth type: MoM or YoY")
    parser.add_argument("--output",      required=True,  help="Path to write the output CSV")
    args = parser.parse_args()

    try:
        dataset = load_dataset(args.input)
        growth_table = compute_growth(dataset, args.ward, args.category, args.growth_type)
        write_output(growth_table, args.output)
        print(f"Done. {len(growth_table)} rows written to '{args.output}'.")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
