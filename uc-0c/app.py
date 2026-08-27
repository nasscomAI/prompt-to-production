"""
UC-0C app.py — Budget Growth Calculator
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse
import csv
import sys

def load_dataset(input_path: str) -> list:
    """
    Reads the budget CSV file, validates the expected schema columns,
    and returns a list of raw records.
    """
    records = []
    expected_fields = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
    
    try:
        with open(input_path, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            
            # Check headers
            headers = reader.fieldnames
            if not headers:
                print("Error: Input CSV is empty.", file=sys.stderr)
                sys.exit(1)
            
            missing_headers = [field for field in expected_fields if field not in headers]
            if missing_headers:
                print(f"Error: Missing expected columns: {', '.join(missing_headers)}", file=sys.stderr)
                sys.exit(1)

            for row in reader:
                records.append(row)
    except FileNotFoundError:
        print(f"Error: Input file not found at {input_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading CSV dataset: {e}", file=sys.stderr)
        sys.exit(1)
        
    return records


def compute_growth(records: list, ward: str, category: str, growth_type: str, output_path: str):
    """
    Filters records, sorts them chronologically, computes growth,
    and writes the growth audit table to output_path.
    """
    # 1. Filter records
    filtered = []
    for r in records:
        if r["ward"].strip() == ward.strip() and r["category"].strip() == category.strip():
            filtered.append(r)

    if not filtered:
        print(f"Warning: No records found for ward '{ward}' and category '{category}'.", file=sys.stderr)

    # 2. Sort chronologically by period (YYYY-MM)
    filtered.sort(key=lambda x: x["period"].strip())

    results = []
    for i, r in enumerate(filtered):
        period = r["period"].strip()
        actual_spend_str = r["actual_spend"].strip()
        raw_notes = r["notes"].strip()

        # Handle current month spend missing
        if not actual_spend_str:
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": "NULL",
                "growth": "NULL",
                "formula": "N/A",
                "notes": raw_notes if raw_notes else "Actual spend is missing."
            })
            continue

        actual_spend = float(actual_spend_str)

        # Handle first month (no previous month for comparison)
        if i == 0:
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": str(actual_spend),
                "growth": "N/A",
                "formula": "N/A",
                "notes": raw_notes
            })
            continue

        # Check previous month spend
        prev_row = filtered[i - 1]
        prev_spend_str = prev_row["actual_spend"].strip()

        if not prev_spend_str:
            # Previous spend was NULL, so cannot compute growth
            prev_notes = prev_row["notes"].strip()
            prev_reason = prev_notes if prev_notes else "missing"
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": str(actual_spend),
                "growth": "NULL",
                "formula": "N/A",
                "notes": f"Previous period actual spend is NULL ({prev_reason})."
            })
            continue

        prev_spend = float(prev_spend_str)

        # Compute growth percentage
        if prev_spend == 0:
            growth_str = "N/A"
            formula_str = f"({actual_spend} - {prev_spend}) / {prev_spend}"
        else:
            growth_val = (actual_spend - prev_spend) / prev_spend
            growth_str = f"{growth_val * 100:+.1f}%"
            formula_str = f"({actual_spend} - {prev_spend}) / {prev_spend}"

        results.append({
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": str(actual_spend),
            "growth": growth_str,
            "formula": formula_str,
            "notes": raw_notes
        })

    # Write output CSV
    try:
        fieldnames = ["period", "ward", "category", "actual_spend", "growth", "formula", "notes"]
        with open(output_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing output growth table to {output_path}: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name")
    parser.add_argument("--category", required=True, help="Category name")
    parser.add_argument("--growth-type", help="Growth type (e.g. MoM)")
    parser.add_argument("--output", required=True, help="Path to write output CSV")
    args = parser.parse_args()

    # Enforcement Rules checking
    if not args.growth_type:
        print("Error: --growth-type must be explicitly specified (e.g. MoM). Refusing to guess.", file=sys.stderr)
        sys.exit(1)

    if args.ward.strip().lower() in ["all", "any", "aggregated", ""]:
        print("Error: Aggregation across multiple wards is prohibited. Refusing to aggregate.", file=sys.stderr)
        sys.exit(1)

    if args.category.strip().lower() in ["all", "any", "aggregated", ""]:
        print("Error: Aggregation across multiple categories is prohibited. Refusing to aggregate.", file=sys.stderr)
        sys.exit(1)

    # Load dataset
    records = load_dataset(args.input)

    # Compute growth and save output
    compute_growth(records, args.ward, args.category, args.growth_type, args.output)
    print(f"Done. Growth output written to {args.output}")


if __name__ == "__main__":
    main()
