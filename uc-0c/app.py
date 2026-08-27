import argparse
import csv
import os
import sys

def load_dataset(input_path: str):
    """
    Reads budget CSV, validates columns, and reports null count and details.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        sys.exit(1)

    dataset = []
    null_rows = []
    required_columns = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]

    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            # Validate columns
            if not all(col in reader.fieldnames for col in required_columns):
                print(f"Error: CSV missing required columns. Found: {reader.fieldnames}")
                sys.exit(1)

            for i, row in enumerate(reader, start=2):
                # Handle actual_spend as float or None
                actual_spend_str = row.get("actual_spend", "").strip()
                if not actual_spend_str:
                    row["actual_spend"] = None
                    null_rows.append((i, row))
                else:
                    try:
                        row["actual_spend"] = float(actual_spend_str)
                    except ValueError:
                        row["actual_spend"] = None
                        null_rows.append((i, row))
                
                dataset.append(row)

        if null_rows:
            print(f"Found {len(null_rows)} deliberate null rows in actual_spend:")
            for line_no, row in null_rows:
                print(f"  - Line {line_no}: {row['period']} | {row['ward']} | {row['category']} | Reason: {row['notes']}")
        
        return dataset

    except Exception as e:
        print(f"Fatal error loading dataset: {e}")
        sys.exit(1)

def compute_growth(dataset, target_ward, target_category, growth_type):
    """
    Calculates growth (MoM) for a specific ward and category, flagging nulls.
    """
    # Filtering
    filtered_data = [
        row for row in dataset 
        if row["ward"] == target_ward and row["category"] == target_category
    ]

    if not filtered_data:
        print(f"Error: No data found for Ward '{target_ward}' and Category '{target_category}'.")
        sys.exit(1)

    # Sort by period to ensure MoM calc is correct
    filtered_data.sort(key=lambda x: x["period"])

    results = []
    for i, row in enumerate(filtered_data):
        period = row["period"]
        actual = row["actual_spend"]
        prev_actual = filtered_data[i-1]["actual_spend"] if i > 0 else None
        
        formula = "n/a (First period)"
        growth_str = "n/a"

        if actual is None:
            growth_str = "NULL_VALD" # Flag for output
            formula = f"NOT COMPUTED - {row['notes']}"
        elif i == 0:
            formula = "n/a (Start of sequence)"
        elif prev_actual is None:
            growth_str = "NOT_COMPUTED"
            formula = f"NOT COMPUTED - Previous period ({filtered_data[i-1]['period']}) had no data"
        else:
            # Growth = (Current - Previous) / Previous
            diff = actual - prev_actual
            growth = (diff / prev_actual) * 100
            growth_str = f"{'+' if growth >= 0 else ''}{growth:.1f}%"
            formula = f"(({actual} - {prev_actual}) / {prev_actual}) * 100"

        results.append({
            "Ward": target_ward,
            "Category": target_category,
            "Period": period,
            "Actual Spend": actual if actual is not None else "NULL",
            "Growth": growth_str,
            "Formula": formula
        })
    
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Analyst")
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--ward", required=False, help="Specific Ward name")
    parser.add_argument("--category", required=False, help="Specific Category name")
    parser.add_argument("--growth-type", required=False, help="Type of growth (e.g. MoM)")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    args = parser.parse_args()

    # Enforcement Rule 4: If growth-type not specified, refuse
    if not args.growth_type:
        print("Error: --growth-type must be specified (e.g., MoM). Guessing is not permitted.")
        sys.exit(1)

    # Enforcement Rule 1: Never aggregate across wards or categories unless explicitly instructed
    if not args.ward or args.ward.lower() == "all":
        print("Error: Ward must be specified. All-ward aggregation is refused.")
        sys.exit(1)
    
    if not args.category or args.category.lower() == "all":
        print("Error: Category must be specified. All-category aggregation is refused.")
        sys.exit(1)

    # Load and validate
    dataset = load_dataset(args.input)

    # Compute
    results = compute_growth(dataset, args.ward, args.category, args.growth_type)

    # Write output
    try:
        fieldnames = ["Ward", "Category", "Period", "Actual Spend", "Growth", "Formula"]
        with open(args.output, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"Success: Growth table written to {args.output}")
    except Exception as e:
        print(f"Error writing output: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
