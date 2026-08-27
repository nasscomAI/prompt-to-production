import argparse
import csv
import os
import sys

def load_dataset(file_path: str):
    """
    Reads CSV, validates columns, and identifies all rows with null actual_spend values.
    """
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        sys.exit(1)
        
    data = []
    null_rows = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2): # 1 is header
            # Normalize numeric fields
            try:
                row['budgeted_amount'] = float(row['budgeted_amount'])
            except ValueError:
                row['budgeted_amount'] = 0.0
                
            actual = row.get('actual_spend', '').strip()
            if not actual:
                row['actual_spend'] = None
                null_rows.append((i, row['ward'], row['category'], row['period'], row['notes']))
            else:
                try:
                    row['actual_spend'] = float(actual)
                except ValueError:
                    row['actual_spend'] = None
                    null_rows.append((i, row['ward'], row['category'], row['period'], row['notes']))
            
            data.append(row)
            
    if null_rows:
        print(f"Warning: Found {len(null_rows)} null records in dataset.")
        for idx, w, c, p, n in null_rows:
            print(f"  - Row {idx} ({p}, {w}, {c}): {n}")
            
    return data

def compute_growth(data, ward, category, growth_type, output_path):
    """
    Computes MoM/YoY growth and writes to CSV.
    """
    # 1. Refusal checks
    if not ward or ward.lower() == "all":
        print("Refusal: I cannot aggregate across all wards. Please specify a single ward.")
        sys.exit(1)
    if not category or category.lower() == "all":
        print("Refusal: I cannot aggregate across all categories. Please specify a single category.")
        sys.exit(1)
    if not growth_type:
        print("Refusal: --growth-type (MoM or YoY) is required. I cannot guess the formula.")
        sys.exit(1)
        
    # 2. Filter data
    filtered = [r for r in data if r['ward'] == ward and r['category'] == category]
    if not filtered:
        print(f"No data found for Ward: {ward}, Category: {category}")
        return
        
    # Sort by period
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    for i, row in enumerate(filtered):
        current_val = row['actual_spend']
        period = row['period']
        notes = row['notes']
        
        res_row = {
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": current_val if current_val is not None else "NULL",
            "growth": "n/a",
            "formula": "n/a"
        }
        
        if growth_type == "MoM":
            if i == 0:
                res_row["growth"] = "n/a (Start of sequence)"
                res_row["formula"] = "n/a"
            elif current_val is None:
                res_row["growth"] = "NULL"
                res_row["formula"] = f"Flagged: {notes}"
            else:
                prev_val = filtered[i-1]['actual_spend']
                if prev_val is None:
                    res_row["growth"] = "NULL"
                    res_row["formula"] = f"Calculation failed: Previous period ({filtered[i-1]['period']}) is NULL"
                else:
                    growth = ((current_val - prev_val) / prev_val) * 100
                    res_row["growth"] = f"{growth:+.1f}%"
                    res_row["formula"] = f"({current_val} - {prev_val}) / {prev_val}"
        else:
             res_row["growth"] = "YoY not fully implemented (requires same month in previous year)"
             res_row["formula"] = "n/a"

        results.append(res_row)

    # 3. Write output
    fieldnames = ["period", "ward", "category", "actual_spend", "growth", "formula"]
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"Growth calculation complete. Results written to {output_path}")

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Analyst")
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", help="MoM or YoY")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    
    dataset = load_dataset(args.input)
    compute_growth(dataset, args.ward, args.category, args.growth_type, args.output)

if __name__ == "__main__":
    main()
