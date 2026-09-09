"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
import sys
from pathlib import Path


def load_dataset(file_path: str):
    path = Path(file_path)
    if not path.exists():
        sys.exit(f"Error: Input file '{file_path}' not found.")

    records = []
    null_rows = []

    with open(path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required_cols = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
        if not required_cols.issubset(reader.fieldnames):
            sys.exit(f"Error: Dataset missing required columns. Must include: {required_cols}")

        for idx, row in enumerate(reader, start=2):
            raw_spend = row["actual_spend"].strip()
            if raw_spend == "" or raw_spend.lower() == "null":
                row["actual_spend_float"] = None
                null_rows.append((idx, row))
            else:
                try:
                    row["actual_spend_float"] = float(raw_spend)
                except ValueError:
                    row["actual_spend_float"] = None
                    null_rows.append((idx, row))
            records.append(row)

    print(f"Dataset loaded: {len(records)} rows found.")
    print(f"Detected {len(null_rows)} null actual_spend rows:")
    for row_num, item in null_rows:
        print(f"  - Line {row_num}: [{item['period']}] {item['ward']} | {item['category']} -> Reason: {item['notes']}")

    return records


def compute_growth(records, target_ward, target_category, growth_type):
    # Enforcement: Never guess growth_type
    if not growth_type:
        sys.exit("Refusal: --growth-type not specified. You must explicitly choose (e.g., 'MoM').")

    if growth_type.upper() != "MOM":
        sys.exit(f"Refusal: Unsupported growth type '{growth_type}'. Only 'MoM' is currently supported.")

    # Enforcement: Must be specific ward and category, no all-ward aggregation
    if not target_ward or not target_category:
        sys.exit("Refusal: Ward and Category must be specified. Aggregation across all wards is strictly forbidden.")

    filtered = [
        r for r in records
        if r["ward"].strip().lower() == target_ward.strip().lower()
        and r["category"].strip().lower() == target_category.strip().lower()
    ]

    if not filtered:
        sys.exit(f"No records found for Ward '{target_ward}' and Category '{target_category}'.")

    # Sort sequentially by period (YYYY-MM)
    filtered.sort(key=lambda x: x["period"])

    results = []
    prev_spend = None

    for r in filtered:
        period = r["period"]
        curr_spend = r["actual_spend_float"]
        notes = r["notes"]

        if curr_spend is None:
            # Enforcement: Flag null rows, do not compute
            results.append({
                "period": period,
                "ward": r["ward"],
                "category": r["category"],
                "actual_spend": "NULL",
                "mom_growth": "FLAGGED_NULL",
                "formula_used": "N/A (Null value - not computed)",
                "notes": notes
            })
            prev_spend = None
        else:
            if prev_spend is None:
                growth_str = "N/A"
                formula = "Baseline period (no previous period available)"
            else:
                growth = ((curr_spend - prev_spend) / prev_spend) * 100
                growth_str = f"{growth:+.1f}%"
                formula = f"(({curr_spend} - {prev_spend}) / {prev_spend}) * 100"

            results.append({
                "period": period,
                "ward": r["ward"],
                "category": r["category"],
                "actual_spend": f"{curr_spend:.1f}",
                "mom_growth": growth_str,
                "formula_used": formula,
                "notes": notes
            })
            prev_spend = curr_spend

    return results


def main():
    parser = argparse.ArgumentParser(description="Compute ward-level infrastructure budget growth.")
    parser.add_argument("--input", required=True, help="Path to input CSV file")
    parser.add_argument("--ward", required=True, help="Specific ward name")
    parser.add_argument("--category", required=True, help="Specific category name")
    parser.add_argument("--growth-type", required=True, help="Growth type (e.g., MoM)")
    parser.add_argument("--output", required=True, help="Path to output CSV file")

    args = parser.parse_args()

    records = load_dataset(args.input)
    growth_results = compute_growth(records, args.ward, args.category, args.growth_type)

    fieldnames = ["period", "ward", "category", "actual_spend", "mom_growth", "formula_used", "notes"]

    output_path = Path(args.output)
    with open(output_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(growth_results)

    print(f"\nGrowth output successfully generated at: {output_path.resolve()}")


if __name__ == "__main__":
    main()
