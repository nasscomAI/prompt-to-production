import argparse
import csv
import sys
import os

def load_dataset(file_path):
    """Reads CSV, validates columns, and reports null rows."""
    if not os.path.exists(file_path):
        print(f"Refusal: File '{file_path}' not found.")
        sys.exit(1)
    
    data = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            required_cols = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
            
            # Check headers
            if not all(col in reader.fieldnames for col in required_cols):
                print(f"Refusal: Missing required columns. Required headers: {required_cols}")
                sys.exit(1)
            
            null_count = 0
            for row in reader:
                # Actual spend is null if empty string
                if not row['actual_spend'].strip():
                    null_count += 1
                    reason = row['notes'] if row['notes'].strip() else "No reason provided"
                    print(f"Null Found: {row['period']} | {row['ward']} | {row['category']} | Reason: {reason}")
                    row['actual_spend'] = None
                else:
                    try:
                        row['actual_spend'] = float(row['actual_spend'])
                    except ValueError:
                        print(f"Refusal: Invalid data in actual_spend for row: {row}")
                        sys.exit(1)
                data.append(row)
            
            if null_count > 0:
                print(f"Total null actual_spend rows identified: {null_count}")
    except Exception as e:
        print(f"Error: Could not read dataset. {e}")
        sys.exit(1)
    
    return data

def compute_growth(dataset, ward, category, growth_type):
    """Computes growth and returns a table with formulas."""
    if growth_type.upper() != "MOM":
        print(f"Refusal: Only 'MoM' growth type is currently supported. Received: {growth_type}")
        sys.exit(1)
        
    # Filter for specific ward and category
    subset = [row for row in dataset if row['ward'] == ward and row['category'] == category]
    
    if not subset:
        print(f"Refusal: No data found for Ward: '{ward}' and Category: '{category}'.")
        sys.exit(1)
    
    # Sort by period
    subset.sort(key=lambda x: x['period'])
    
    results = []
    prev_spend = None
    
    for row in subset:
        curr_spend = row['actual_spend']
        period = row['period']
        
        result_row = {
            "Ward": ward,
            "Category": category,
            "Period": period,
            "Actual Spend": curr_spend if curr_spend is not None else "NULL",
            "Growth": "N/A",
            "Formula": "N/A"
        }
        
        if curr_spend is None:
            reason = row['notes'] if row['notes'].strip() else "Null value"
            result_row["Growth"] = f"NULL - {reason}"
            result_row["Formula"] = "Calculation skipped due to null value"
        elif prev_spend is not None:
            if prev_spend == 0:
                result_row["Growth"] = "Inf (Prev was 0)"
                result_row["Formula"] = f"(({curr_spend} - 0) / 0) * 100"
            else:
                growth = ((curr_spend - prev_spend) / prev_spend) * 100
                result_row["Growth"] = f"{growth:+.1f}%"
                result_row["Formula"] = f"(({curr_spend} - {prev_spend}) / {prev_spend}) * 100"
        elif prev_spend is None:
             result_row["Growth"] = "N/A (First Period)"
             result_row["Formula"] = "Initial entry"

        results.append(result_row)
        prev_spend = curr_spend
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Analyst")
    parser.add_argument("--input", required=True, help="Path to input budget CSV")
    parser.add_argument("--ward", help="Target ward for analysis")
    parser.add_argument("--category", help="Target category for analysis")
    parser.add_argument("--growth-type", help="Type of growth (e.g. MoM)")
    parser.add_argument("--output", required=True, help="Path to save output CSV")
    
    args = parser.parse_args()
    
    # Enforcement Rule 4: If --growth-type not specified — refuse and ask
    if not args.growth_type:
        print("Refusal: --growth-type must be specified. Do you want 'MoM' or 'YoY'?")
        sys.exit(1)
        
    # Enforcement Rule 1: Never aggregate across wards or categories
    if not args.ward or not args.category or args.ward.lower() == "all" or args.category.lower() == "all":
        print("Refusal: Analysis must be restricted to a single ward and single category. Aggregation is not permitted.")
        sys.exit(1)
        
    dataset = load_dataset(args.input)
    results = compute_growth(dataset, args.ward, args.category, args.growth_type)
    
    # Write output to CSV
    try:
        with open(args.output, 'w', newline='', encoding='utf-8') as f:
            if results:
                writer = csv.DictWriter(f, fieldnames=results[0].keys())
                writer.writeheader()
                writer.writerows(results)
        print(f"Success: Growth output saved to {args.output}")
    except Exception as e:
        print(f"Error: Could not write output. {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
