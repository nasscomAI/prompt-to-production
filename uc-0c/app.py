import argparse
import csv
import sys
from datetime import datetime

def load_dataset(input_path: str) -> list:
    """
    Reads CSV, validates columns, reports null count and identifies null rows.
    """
    mandatory_columns = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
    data = []
    null_rows = []
    
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            # Validate columns
            if not all(col in reader.fieldnames for col in mandatory_columns):
                missing = [col for col in mandatory_columns if col not in reader.fieldnames]
                print(f"Error: Missing mandatory columns: {', '.join(missing)}")
                sys.exit(1)
            
            for row in reader:
                # Check for null actual_spend
                if not row["actual_spend"] or row["actual_spend"].strip() == "":
                    null_rows.append(row)
                data.append(row)
                
        if null_rows:
            print(f"Found {len(null_rows)} rows with null actual_spend:")
            for nr in null_rows:
                print(f" - {nr['period']} | {nr['ward']} | {nr['category']} | Reason: {nr['notes']}")
        else:
            print("No null values found in the dataset.")
            
    except FileNotFoundError:
        print(f"Error: Dataset file {input_path} not found.")
        sys.exit(1)
        
    return data

def compute_growth(data: list, ward: str, category: str, growth_type: str) -> list:
    """
    Calculates growth (MoM) for a specific ward and category.
    """
    # Filter for specific ward and category
    filtered = [row for row in data if row["ward"] == ward and row["category"] == category]
    
    if not filtered:
        print(f"Error: No data found for Ward: '{ward}' and Category: '{category}'.")
        return []
    
    # Sort by period
    filtered.sort(key=lambda x: x["period"])
    
    results = []
    for i in range(len(filtered)):
        current = filtered[i]
        period = current["period"]
        actual_spend_str = current["actual_spend"]
        
        row_result = {
            "period": period,
            "actual_spend": actual_spend_str,
            "growth": "n/a",
            "formula": "n/a"
        }
        
        # Handle null values
        if not actual_spend_str or actual_spend_str.strip() == "":
            row_result["growth"] = "NULL"
            row_result["formula"] = f"Calculation skipped: {current['notes']}"
            results.append(row_result)
            continue
            
        # Growth calculation (only if not first row and previous is not null)
        if i > 0:
            previous = filtered[i-1]
            prev_spend_str = previous["actual_spend"]
            
            if prev_spend_str and prev_spend_str.strip() != "":
                curr_val = float(actual_spend_str)
                prev_val = float(prev_spend_str)
                
                if prev_val != 0:
                    growth = ((curr_val - prev_val) / prev_val) * 100
                    row_result["growth"] = f"{growth:+.1f}%"
                    row_result["formula"] = f"({curr_val} - {prev_val}) / {prev_val}"
                else:
                    row_result["growth"] = "inf"
                    row_result["formula"] = "Division by zero (previous spend was 0)"
            else:
                row_result["growth"] = "n/a"
                row_result["formula"] = "Previous period data is NULL"
                
        results.append(row_result)
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Analyst")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name (must match exactly)")
    parser.add_argument("--category", required=True, help="Category name (must match exactly)")
    parser.add_argument("--growth-type", required=True, help="Growth calculation type (MoM/YoY)")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()
    
    # Enforcement: Growth type check
    if args.growth_type not in ["MoM", "YoY"]:
        print(f"Error: Unknown growth-type '{args.growth_type}'. Refusing to guess.")
        sys.exit(1)
        
    # Enforcement: No aggregation check (implicit by mandatory arguments)
    print(f"Starting analysis for {args.ward} | {args.category}...")
    
    data = load_dataset(args.input)
    results = compute_growth(data, args.ward, args.category, args.growth_type)
    
    if results:
        with open(args.output, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["period", "actual_spend", "growth", "formula"])
            writer.writeheader()
            writer.writerows(results)
        print(f"Analysis complete. Results written to {args.output}")

if __name__ == "__main__":
    main()
