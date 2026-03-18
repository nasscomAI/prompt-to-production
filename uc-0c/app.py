"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
import sys

def load_dataset(file_path: str) -> tuple[list, list]:
    """
    Reads the budget CSV, validates columns, and reports null rows before returning data.
    """
    required_cols = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
    data = []
    null_rows_manifest = []

    try:
        with open(file_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames or not required_cols.issubset(set(reader.fieldnames)):
                raise ValueError(f"Missing required columns in CSV. Expected {required_cols}")

            for i, row in enumerate(reader, start=2): # 1 is header
                data.append(row)
                
                # Check for genuinely empty/null values, handling whitespaces
                val = row.get("actual_spend", "").strip()
                if not val or val.lower() == "null":
                    null_rows_manifest.append(row)
                    
    except FileNotFoundError:
        print(f"Error: Dataset not found at {file_path}")
        sys.exit(1)
        
    print(f"Dataset loaded. Discovered {len(null_rows_manifest)} rows with null actual_spend.")
    for row in null_rows_manifest:
        print(f" - [NULL FLAG] {row['period']} | {row['ward']} | {row['category']} | Reason: {row.get('notes', 'Unknown')}")
        
    return data, null_rows_manifest


def compute_growth(data: list, ward: str, category: str, growth_type: str) -> list:
    """
    Calculates growth metric per-ward and per-category, including the explicit formula used.
    """
    # Rule 1: Never aggregate across wards or categories unless explicitly instructed (we'll just refuse outright here per rules)
    if not ward or not category:
        print("ERROR: Aggregation across multiple wards or categories is strictly forbidden by policy. You must specify exact --ward and --category.")
        sys.exit(1)

    # Filter data strictly by ward and category
    filtered_data = [row for row in data if row.get("ward") == ward and row.get("category") == category]
    
    # Sort chronologically
    filtered_data.sort(key=lambda x: x.get("period", ""))

    output_table = []
    previous_spend = None
    
    # Logic note: MoM natively compares period N to N-1
    # For YoY, this simplistic script assumes a 12-month jump, but we'll focus on the requested MoM as per README example
    
    for row in filtered_data:
        period = row.get("period")
        notes = row.get("notes", "")
        spend_str = row.get("actual_spend", "").strip()
        
        # Rule 2: Flag every null row before computing any metrics
        if not spend_str or spend_str.lower() == "null":
            output_table.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": "NULL",
                "computed_growth": "Must be flagged — not computed",
                "formula": f"Calculation bypassed. Reason: {notes}"
            })
            previous_spend = None # Break the chain for context
            continue
            
        try:
            current_spend = float(spend_str)
        except ValueError:
            current_spend = 0.0
            
        # Rule 3: Show the exact formula
        if growth_type.upper() == "MOM":
            if previous_spend is not None and previous_spend != 0:
                growth_val = ((current_spend - previous_spend) / previous_spend) * 100
                formula_str = f"(({current_spend} - {previous_spend}) / {previous_spend}) * 100"
                growth_metric = f"{growth_val:+.1f}%"
            else:
                growth_metric = "n/a"
                formula_str = "No prior period valid data to compute MoM"
        else:
            # Fallback for YoY or anything else requested
            growth_metric = "n/a"
            formula_str = f"Formula not natively supported for {growth_type}"

        output_table.append({
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": current_spend,
            "computed_growth": growth_metric,
            "formula": formula_str
        })
        
        previous_spend = current_spend

    return output_table

def main():
    parser = argparse.ArgumentParser(description="UC-0C Financial Data Analyst")
    parser.add_argument("--input", required=True, help="Path to budget CSV data")
    parser.add_argument("--ward", required=False, help="Specific ward to analyze")
    parser.add_argument("--category", required=False, help="Specific category to analyze")
    parser.add_argument("--growth-type", required=False, help="Growth type (e.g. MoM, YoY)")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    args = parser.parse_args()

    # Rule 4: Refuse if --growth-type not specified 
    if not args.growth_type:
        print("ERROR: --growth-type argument is not specified. I cannot guess or assume a default growth type. Please provide --growth-type.")
        sys.exit(1)

    data, null_rows = load_dataset(args.input)
    
    results = compute_growth(data, args.ward, args.category, args.growth_type)
    
    with open(args.output, mode="w", newline="", encoding="utf-8") as f:
        fieldnames = ["period", "ward", "category", "actual_spend", "computed_growth", "formula"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
        
    print(f"Success. Wrote {len(results)} rows to {args.output}")


if __name__ == "__main__":
    main()
