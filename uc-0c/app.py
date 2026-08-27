"""
UC-0C — Budget Analyst
Traceable growth calculations with explicit formula enforcement and null-flagging.
"""
import argparse
import csv
import os

def load_dataset(input_path: str, ward: str, category: str) -> list:
    """
    Skill: load_dataset — reads CSV, filters by ward/category, and returns data for processing.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Missing input file: {input_path}")
        
    filtered_rows = []
    with open(input_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Enforcement: Stay within ward/category silo
            if row['ward'] == ward and row['category'] == category:
                filtered_rows.append(row)
                
    # Sort chronologically
    filtered_rows.sort(key=lambda x: x['period'])
    return filtered_rows

def compute_growth(rows: list, growth_type: str) -> list:
    """
    Skill: compute_growth — calculates MoM growth and enforces formula transparency.
    """
    results = []
    for i, row in enumerate(rows):
        period = row['period']
        actual_raw = row['actual_spend']
        notes = row['notes']
        
        current_val = None
        if actual_raw and actual_raw.strip():
            try:
                current_val = float(actual_raw)
            except ValueError:
                current_val = None
        
        growth_value = "n/a"
        formula_str = "n/a"
        
        # Enforcement: Flag nulls and cite notes
        if current_val is None:
            growth_value = f"NULL: {notes if notes else 'Data missing'}"
            formula_str = "Calculation skipped due to missing data"
        elif i > 0:
            prev_row = rows[i-1]
            prev_actual_raw = prev_row['actual_spend']
            
            prev_val = None
            if prev_actual_raw and prev_actual_raw.strip():
                try:
                    prev_val = float(prev_actual_raw)
                except ValueError:
                    prev_val = None
            
            # MoM calculation
            if prev_val is not None:
                growth = ((current_val - prev_val) / prev_val) * 100
                growth_value = f"{growth:+.1f}%"
                # Enforcement: Show formula used
                formula_str = f"(({current_val} - {prev_val}) / {prev_val}) * 100"
            else:
                growth_value = "n/a (Previous value missing)"
                formula_str = "n/a"
        
        results.append({
            "period": period,
            "ward": row["ward"],
            "category": row["category"],
            "actual_spend": actual_raw if actual_raw else "NULL",
            "growth": growth_value,
            "formula": formula_str
        })
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Analyst")
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True) # Enforcement: Must be specified
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    
    # Enforcement: Verify growth type
    if args.growth_type not in ["MoM", "YoY"]:
        print(f"Error: Unsupported growth-type '{args.growth_type}'. Must be MoM or YoY.")
        return

    try:
        data = load_dataset(args.input, args.ward, args.category)
        if not data:
            print(f"No records found for Ward: {args.ward}, Category: {args.category}")
            return
            
        final_results = compute_growth(data, args.growth_type)
        
        # Write to CSV
        file_exists = os.path.exists(args.output)
        with open(args.output, mode='a', encoding='utf-8', newline='') as f:
            fieldnames = ["period", "ward", "category", "actual_spend", "growth", "formula"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerows(final_results)
            
        print(f"Success: Processed {args.ward} | {args.category}")
        
    except Exception as e:
        print(f"Error in processing: {e}")

if __name__ == "__main__":
    main()
