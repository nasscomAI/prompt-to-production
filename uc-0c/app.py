"""
UC-0C — Number That Looks Right
Compute per-ward, per-category MoM growth for actual_spend, handling nulls explicitly.
"""
import argparse
import csv
import sys

def compute_growth_table(input_path, ward, category, growth_type, output_path):
    rows = []
    try:
        with open(input_path, "r", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                if row["ward"] == ward and row["category"] == category:
                    rows.append(row)
    except Exception as e:
        print(f"Error reading input file: {e}", file=sys.stderr)
        return
    if not rows:
        print(f"No rows found for ward '{ward}' and category '{category}'.", file=sys.stderr)
        return
    rows.sort(key=lambda r: r["period"])
    output = []
    prev_spend = None
    for r in rows:
        period = r["period"]
        actual_spend = r["actual_spend"]
        notes = r.get("notes", "")
        null_flag = ""
        null_reason = ""
        if actual_spend == "" or actual_spend is None:
            null_flag = "NULL"
            null_reason = notes if notes else "No explanation for null actual_spend"
            mom_growth = "NEEDS_REVIEW"
        else:
            try:
                actual_spend = float(actual_spend)
                if prev_spend is not None:
                    mom_growth = round(actual_spend - prev_spend, 2)
                else:
                    mom_growth = "NA"
                prev_spend = actual_spend
            except Exception:
                mom_growth = "NEEDS_REVIEW"
                null_flag = "NULL"
                null_reason = "Invalid actual_spend value"
        output.append({
            "period": period,
            "ward": ward,
            "category": category,
            "MoM_growth": mom_growth,
            "null_flag": null_flag,
            "null_reason": null_reason
        })
    try:
        with open(output_path, "w", encoding="utf-8", newline="") as outfile:
            fieldnames = ["period", "ward", "category", "MoM_growth", "null_flag", "null_reason"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in output:
                writer.writerow(row)
    except Exception as e:
        print(f"Error writing output file: {e}", file=sys.stderr)
        return
    print(f"Done. Growth table written to {output_path}")

def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Analysis")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name")
    parser.add_argument("--category", required=True, help="Category name")
    parser.add_argument("--growth-type", required=True, help="Growth type (MoM)")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()
    compute_growth_table(args.input, args.ward, args.category, args.growth_type, args.output)
    rows.sort(key=lambda r: r["period"])  # Sort by period
    output = []
    prev_spend = None
    for r in rows:
        period = r["period"]
        actual_spend = r["actual_spend"]
        notes = r.get("notes", "")
        null_flag = ""
        null_reason = ""
        if actual_spend == "" or actual_spend is None:
            null_flag = "NULL"
            null_reason = notes if notes else "No explanation for null actual_spend"
            mom_growth = "NEEDS_REVIEW"
        else:
            try:
                actual_spend = float(actual_spend)
                if prev_spend is not None:
                    mom_growth = round(actual_spend - prev_spend, 2)
                else:
                    mom_growth = "NA"
                prev_spend = actual_spend
            except Exception:
                mom_growth = "NEEDS_REVIEW"
                null_flag = "NULL"
                null_reason = "Invalid actual_spend value"
        output.append({
            "period": period,
            "ward": ward,
            "category": category,
            "MoM_growth": mom_growth,
            "null_flag": null_flag,
            "null_reason": null_reason
        })
    try:
        with open(output_path, "w", encoding="utf-8", newline="") as outfile:
            fieldnames = ["period", "ward", "category", "MoM_growth", "null_flag", "null_reason"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in output:
                writer.writerow(row)
    except Exception as e:
        print(f"Error writing output file: {e}", file=sys.stderr)
        return
    print(f"Done. Growth table written to {output_path}")

def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Analysis")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name")
    parser.add_argument("--category", required=True, help="Category name")
    parser.add_argument("--growth-type", required=True, help="Growth type (MoM)")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()
    compute_growth_table(args.input, args.ward, args.category, args.growth_type, args.output)

if __name__ == "__main__":
    main()
