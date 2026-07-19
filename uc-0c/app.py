"""
UC-0C — Number That Looks Right
Calculates budget growth metrics per-ward and per-category.
"""
import argparse
import csv
import sys
import os

def load_dataset(input_path: str) -> list:
    """
    Read CSV and validate required columns.
    Prints information about the deliberate null rows.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found at {input_path}")

    required_columns = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
    rows = []
    null_rows = []

    with open(input_path, mode="r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        if not required_columns.issubset(set(reader.fieldnames or [])):
            raise ValueError(f"CSV must contain columns: {required_columns}")
        
        for idx, row in enumerate(reader, start=2):
            spend = row.get("actual_spend", "").strip()
            if spend == "":
                null_rows.append((idx, row.get("period"), row.get("ward"), row.get("category"), row.get("notes")))
            rows.append(row)

    print(f"Dataset loaded. Total rows: {len(rows)}")
    print(f"Identified {len(null_rows)} null spend rows:")
    for idx, period, ward, cat, notes in null_rows:
        print(f"  Line {idx}: Period={period}, Ward={ward}, Category={cat}, Reason={notes}")

    return rows

def compute_growth(rows: list, ward: str, category: str, growth_type: str) -> list:
    """
    Filter data by ward and category, and compute MoM growth chronologically.
    """
    # Refusal logic
    if not ward or ward.lower() == "all":
        sys.stderr.write("Error: Aggregation across multiple wards is not permitted. Please specify a single ward.\n")
        sys.exit(1)
    if not category or category.lower() == "all":
        sys.stderr.write("Error: Aggregation across multiple categories is not permitted. Please specify a single category.\n")
        sys.exit(1)
    if not growth_type:
        sys.stderr.write("Error: Growth type must be specified. Please specify --growth-type (e.g. MoM).\n")
        sys.exit(1)
    if growth_type != "MoM":
        sys.stderr.write(f"Error: Unsupported growth type '{growth_type}'. Only MoM is supported.\n")
        sys.exit(1)

    # Filter rows matching ward and category
    filtered_rows = [r for r in rows if r["ward"].strip() == ward.strip() and r["category"].strip() == category.strip()]
    
    # Sort chronologically by period
    filtered_rows.sort(key=lambda x: x["period"])

    if not filtered_rows:
        sys.stderr.write(f"Warning: No rows found matching Ward='{ward}' and Category='{category}'\n")

    output_rows = []
    for idx, row in enumerate(filtered_rows):
        period = row["period"]
        curr_spend_str = row["actual_spend"].strip()
        notes = row["notes"].strip()

        # Check if current month spend is null
        if curr_spend_str == "":
            growth_val = f"NULL (Flagged: {notes})"
            formula = "n/a"
            actual_spend = "NULL"
        else:
            actual_spend = float(curr_spend_str)
            if idx == 0:
                # First month has no previous month
                growth_val = "n/a"
                formula = "n/a"
            else:
                prev_row = filtered_rows[idx - 1]
                prev_spend_str = prev_row["actual_spend"].strip()
                if prev_spend_str == "":
                    growth_val = "NULL (Flagged: Previous month actual_spend is null)"
                    formula = "n/a"
                else:
                    prev_spend = float(prev_spend_str)
                    if prev_spend == 0:
                        growth_val = "n/a"
                        formula = f"(({actual_spend} - 0.0) / 0.0) * 100"
                    else:
                        pct_change = ((actual_spend - prev_spend) / prev_spend) * 100
                        sign = "+" if pct_change > 0 else ""
                        growth_val = f"{sign}{pct_change:.1f}%"
                        formula = f"(({actual_spend} - {prev_spend}) / {prev_spend}) * 100"

        output_rows.append({
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": actual_spend,
            "growth": growth_val,
            "formula": formula
        })

    return output_rows

def write_output(results: list, output_path: str):
    """
    Write growth results to CSV.
    """
    fieldnames = ["period", "ward", "category", "actual_spend", "growth", "formula"]
    with open(output_path, mode="w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow(row)
    print(f"Results successfully written to {output_path}")

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=False, help="Ward name")
    parser.add_argument("--category", required=False, help="Category name")
    parser.add_argument("--growth-type", required=False, help="Growth type (e.g. MoM)")
    parser.add_argument("--output", required=True, help="Path to write output CSV")
    args = parser.parse_args()

    # If args are missing, handle refusal rules
    if not args.ward or not args.category or not args.growth_type:
        sys.stderr.write("Error: --ward, --category, and --growth-type must all be specified to prevent improper aggregation.\n")
        sys.exit(1)

    rows = load_dataset(args.input)
    results = compute_growth(rows, args.ward, args.category, args.growth_type)
    write_output(results, args.output)

if __name__ == "__main__":
    main()
