"""
UC-0C app.py — Ward budget growth calculator.
Implements load_dataset and compute_growth skills from skills.md.
Enforces all rules from agents.md.
"""
import argparse
import csv
import os
import sys


def load_dataset(file_path):
    if not os.path.exists(file_path):
        return None, None, f"Error: File not found at {file_path}"

    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            return None, None, "Error: CSV file is empty"
        required = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
        missing = [c for c in required if c not in reader.fieldnames]
        if missing:
            return None, None, f"Error: CSV is missing required columns: {', '.join(missing)}"

        rows = list(reader)

    if not rows:
        return None, None, "Error: CSV file is empty"

    null_rows = []
    for row in rows:
        if row["actual_spend"].strip() == "":
            null_rows.append({
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "reason": row["notes"].strip() if row["notes"].strip() else "No reason provided",
            })

    print(f"Loaded {len(rows)} rows from {file_path}")
    print(f"Null actual_spend rows found: {len(null_rows)}")
    for nr in null_rows:
        print(f"  - {nr['period']} · {nr['ward']} · {nr['category']}: {nr['reason']}")

    return rows, null_rows, None


def compute_growth(ward, category, growth_type, dataset):
    valid_types = {"MoM"}
    if growth_type not in valid_types:
        return None, f"Error: Unsupported growth type '{growth_type}'. Supported: {', '.join(valid_types)}"

    filtered = [r for r in dataset if r["ward"] == ward and r["category"] == category]
    if not filtered:
        return None, f"Error: Ward '{ward}' or category '{category}' not found in data"

    filtered.sort(key=lambda r: r["period"])

    results = []
    for i, row in enumerate(filtered):
        period = row["period"]
        spend_str = row["actual_spend"].strip()
        notes = row["notes"].strip()

        if spend_str == "":
            results.append({
                "period": period,
                "actual_spend": "",
                "previous_period_spend": "",
                "growth_percentage": "",
                "formula_used": "",
                "null_flag": notes if notes else "NULL — no reason provided",
            })
            continue

        current = float(spend_str)

        if i == 0:
            results.append({
                "period": period,
                "actual_spend": str(current),
                "previous_period_spend": "",
                "growth_percentage": "",
                "formula_used": "N/A — first period",
                "null_flag": "",
            })
            continue

        prev_row = filtered[i - 1]
        prev_spend_str = prev_row["actual_spend"].strip()

        if prev_spend_str == "":
            results.append({
                "period": period,
                "actual_spend": str(current),
                "previous_period_spend": "",
                "growth_percentage": "",
                "formula_used": "N/A — previous period is null",
                "null_flag": "Previous period null",
            })
            continue

        previous = float(prev_spend_str)
        growth = ((current - previous) / previous) * 100
        formula = f"MoM: ({current} - {previous}) / {previous} * 100 = {growth:.1f}%"

        results.append({
            "period": period,
            "actual_spend": str(current),
            "previous_period_spend": str(previous),
            "growth_percentage": f"{growth:.1f}%",
            "formula_used": formula,
            "null_flag": "",
        })

    return results, None


def write_output(results, output_path):
    fieldnames = ["period", "actual_spend", "previous_period_spend", "growth_percentage", "formula_used", "null_flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    print(f"Output written to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="UC-0C Ward Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name (e.g. 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=True, help="Category (e.g. 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", required=True, help="Growth type (e.g. MoM)")
    parser.add_argument("--output", required=True, help="Output CSV file path")
    args = parser.parse_args()

    rows, null_rows, error = load_dataset(args.input)
    if error:
        print(error, file=sys.stderr)
        sys.exit(1)

    results, error = compute_growth(args.ward, args.category, args.growth_type, rows)
    if error:
        print(error, file=sys.stderr)
        sys.exit(1)

    write_output(results, args.output)

    print(f"\nGrowth results for {args.ward} / {args.category} ({args.growth_type}):")
    for r in results:
        flag = f" [NULL: {r['null_flag']}]" if r["null_flag"] else ""
        growth = r["growth_percentage"] if r["growth_percentage"] else "N/A"
        print(f"  {r['period']}: {growth}{flag}")


if __name__ == "__main__":
    main()
