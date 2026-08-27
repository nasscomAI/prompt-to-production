import argparse
import csv
import os

def load_dataset(input_path: str, target_ward: str, target_category: str):
    """Reads and filters the budget CSV, reporting nulls found."""
    data = []
    null_rows = []
    
    if not os.path.exists(input_path):
        print(f"Error: Initial file {input_path} not found.")
        return [], []

    with open(input_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Check for illegal aggregation (Implicitly handled by filtering here)
            if row['ward'] == target_ward and row['category'] == target_category:
                # Handle null actual_spend
                if not row['actual_spend'] or row['actual_spend'].strip() == "":
                    null_rows.append(row)
                    row['actual_spend'] = None
                else:
                    row['actual_spend'] = float(row['actual_spend'])
                data.append(row)
    
    # Report nulls found in the filtered set
    for nr in null_rows:
        print(f"Flagging Null: {nr['period']} | {nr['ward']} | {nr['category']} | Reason: {nr['notes']}")
        
    return data, null_rows

def compute_growth(data: list, growth_type: str):
    """Calculates growth and injects formulas into the result."""
    if not growth_type:
        raise ValueError("Growth type not specified. Please choose 'MoM'.")
    
    if growth_type != "MoM":
        raise ValueError(f"Growth type '{growth_type}' is not supported. Use 'MoM'.")

    # Sort data by period to ensure correct MoM calculation
    data.sort(key=lambda x: x['period'])
    results = []
    
    for i in range(len(data)):
        current = data[i]
        prev = data[i-1] if i > 0 else None
        
        row_result = {
            "period": current['period'],
            "ward": current['ward'],
            "category": current['category'],
            "actual_spend": "NULL" if current['actual_spend'] is None else current['actual_spend'],
            "growth": "n/a",
            "formula": "n/a"
        }
        
        if prev and current['actual_spend'] is not None and prev['actual_spend'] is not None:
            c_val = current['actual_spend']
            p_val = prev['actual_spend']
            if p_val != 0:
                growth_val = ((c_val - p_val) / p_val) * 100
                row_result["growth"] = f"{growth_val:+.1f}%"
                row_result["formula"] = f"(({c_val} - {p_val}) / {p_val}) * 100"
            else:
                row_result["growth"] = "inf"
                row_result["formula"] = "Division by zero (Prior=0)"
        elif current['actual_spend'] is None:
            row_result["growth"] = "FLAGGED"
            row_result["formula"] = f"Calculation skipped: {current['notes']}"
        elif i == 0:
            row_result["growth"] = "n/a"
            row_result["formula"] = "First period in dataset"
            
        results.append(row_result)
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Analyst")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Target Ward name")
    parser.add_argument("--category", required=True, help="Target Category name")
    parser.add_argument("--growth-type", help="MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    if not args.growth_type:
        print("Refusal: Growth type (--growth-type) is missing. Please specify 'MoM'.")
        return

    # Load and filter
    data, _ = load_dataset(args.input, args.ward, args.category)
    if not data:
        print(f"No data found for Ward: {args.ward}, Category: {args.category}")
        return
        
    # Compute
    results = compute_growth(data, args.growth_type)
    
    # Write output
    if results:
        keys = results[0].keys()
        with open(args.output, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(results)
        print(f"Done. Results written to {args.output}")

if __name__ == "__main__":
    main()
