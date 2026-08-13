"""
UC-0C app.py — Metadata-Aware Agentic Numerical Analysis
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse
import csv
import os
import sys

def load_and_validate_dataset(filepath: str) -> list:
    """
    Reads the CSV, validates columns and schema, and returns the rows as a list of dicts.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Input file {filepath} not found.")

    expected_columns = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
    rows = []

    with open(filepath, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames if reader.fieldnames else []

        # Check schema
        for col in expected_columns:
            if col not in headers:
                raise ValueError(f"Schema validation failed: missing column '{col}'.")

        for row_idx, row in enumerate(reader, start=1):
            rows.append(row)

    return rows

def compute_growth(rows: list, ward: str, category: str, growth_type: str) -> list:
    """
    Filters data for a specific ward and category, sorts by period,
    and computes growth deterministically showing formulas and handling NULLs.
    """
    if not growth_type:
        raise ValueError("Growth type not specified. Refusing to calculate.")
    if growth_type != "MoM":
        raise ValueError(f"Unsupported growth type '{growth_type}'. Only 'MoM' is supported currently.")

    # Filter by ward and category
    filtered = [r for r in rows if r["ward"] == ward and r["category"] == category]
    if not filtered:
        raise ValueError(f"No records found for Ward: '{ward}', Category: '{category}'.")

    # Sort chronologically by period
    filtered.sort(key=lambda x: x["period"])

    results = []
    for i, curr in enumerate(filtered):
        period = curr["period"]
        budgeted = curr["budgeted_amount"]
        actual_curr_raw = curr["actual_spend"].strip()
        notes = curr["notes"].strip()

        # Initialize output fields
        mom_growth = "N/A"
        formula = "N/A"

        # Check if current is NULL
        if not actual_curr_raw or actual_curr_raw.upper() == "NULL":
            mom_growth = f"N/A - current value is NULL ({notes})"
            formula = "N/A"
        elif i == 0:
            mom_growth = "N/A - first period"
            formula = "N/A"
        else:
            prev = filtered[i - 1]
            actual_prev_raw = prev["actual_spend"].strip()
            prev_notes = prev["notes"].strip()

            # Check if previous is NULL
            if not actual_prev_raw or actual_prev_raw.upper() == "NULL":
                mom_growth = f"N/A - previous value is NULL ({prev_notes})"
                formula = "N/A"
            else:
                try:
                    curr_val = float(actual_curr_raw)
                    prev_val = float(actual_prev_raw)

                    if prev_val == 0:
                        mom_growth = "N/A - zero denominator"
                        formula = f"(({curr_val} - 0) / 0) * 100"
                    else:
                        pct = ((curr_val - prev_val) / prev_val) * 100
                        mom_growth = f"{pct:+.1f}%"
                        formula = f"(({curr_val} - {prev_val}) / {prev_val}) * 100"
                except ValueError:
                    mom_growth = "N/A - invalid numeric values"
                    formula = "N/A"

        results.append({
            "period": period,
            "ward": ward,
            "category": category,
            "budgeted_amount": budgeted,
            "actual_spend": curr["actual_spend"] if curr["actual_spend"] else "NULL",
            "formula": formula,
            "mom_growth": mom_growth,
            "notes": notes
        })

    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Number That Looks Right")
    parser.add_argument("--input", required=True, help="Path to input budget CSV file")
    parser.add_argument("--ward", required=True, help="Specific ward to analyze (refuses aggregation if missing)")
    parser.add_argument("--category", required=True, help="Specific category to analyze (refuses aggregation if missing)")
    parser.add_argument("--growth-type", required=True, help="Growth type to compute (e.g. MoM)")
    parser.add_argument("--output", required=True, help="Path to write results CSV")

    args = parser.parse_args()

    # Enforce strict refusal of broad aggregation
    if not args.ward or args.ward.strip() == "":
        print("Error: Ward is required. Refusing to calculate all-ward aggregation.", file=sys.stderr)
        sys.exit(1)

    if not args.category or args.category.strip() == "":
        print("Error: Category is required. Refusing to calculate all-category aggregation.", file=sys.stderr)
        sys.exit(1)

    print(f"Loading and validating dataset: {args.input}")
    try:
        rows = load_and_validate_dataset(args.input)
    except Exception as e:
        print(f"Error loading dataset: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Calculating growth for Ward: '{args.ward}', Category: '{args.category}' using type '{args.growth_type}'...")
    try:
        results = compute_growth(rows, args.ward, args.category, args.growth_type)
    except Exception as e:
        print(f"Calculation error: {e}", file=sys.stderr)
        sys.exit(1)

    # Ensure output directory exists
    out_dir = os.path.dirname(args.output)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    output_fields = ["period", "ward", "category", "budgeted_amount", "actual_spend", "formula", "mom_growth", "notes"]
    with open(args.output, mode="w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=output_fields)
        writer.writeheader()
        for r in results:
            writer.writerow(r)

    print(f"Numerical analysis written successfully to {args.output}")

if __name__ == "__main__":
    main()
