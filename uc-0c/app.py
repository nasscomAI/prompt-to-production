import argparse
import csv
import sys
import os

def load_dataset(input_path):
    """
    Reads the CSV and validates its presence.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found at {input_path}")
    
    data = []
    with open(input_path, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    return data

def compute_growth(data, ward, category, growth_type):
    """
    Calculates growth while preserving formula transparency and handling nulls.
    """
    # Filter data for the specific ward and category (Anti-aggregation)
    filtered = [r for r in data if r['ward'] == ward and r['category'] == category]
    
    if not filtered:
        return []
        
    # Sort by period to ensure correct MoM calculation
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    for i, row in enumerate(filtered):
        period = row['period']
        actual = row['actual_spend'].strip()
        notes = row.get('notes', '').strip()
        
        result_row = {
            "ward": ward,
            "category": category,
            "period": period,
            "actual_spend": actual if actual else "NULL",
            "growth_percentage": "n/a",
            "formula": "n/a",
            "status": "OK"
        }
        
        # 2. Flag null rows before computing
        if not actual:
            result_row["status"] = f"FLAGGED: {notes}"
            results.append(result_row)
            continue
            
        # 3. Compute growth and show formula
        if growth_type == "MoM":
            if i > 0:
                prev_row = filtered[i-1]
                prev_actual = prev_row['actual_spend'].strip()
                
                if prev_actual:
                    curr_val = float(actual)
                    prev_val = float(prev_actual)
                    growth = ((curr_val - prev_val) / prev_val) * 100
                    result_row["growth_percentage"] = f"{growth:+.1f}%"
                    result_row["formula"] = f"(({curr_val} - {prev_val}) / {prev_val}) * 100"
                else:
                    result_row["status"] = "SKIPPED: Previous period was NULL"
                    result_row["formula"] = "Cannot compute MoM with NULL base"
            else:
                result_row["formula"] = "First period in series"
        
        results.append(result_row)
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Ward Budget Analyst")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Specific ward name")
    parser.add_argument("--category", required=True, help="Specific category name")
    parser.add_argument("--growth-type", help="MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    
    args = parser.parse_args()
    
    # 4. Refusal condition for missing growth-type
    if not args.growth_type:
        print("Error: Calculation refused. You must specify --growth-type (MoM or YoY).")
        sys.exit(1)
        
    # 1. Refusal condition for aggregation
    if args.ward.lower() in ["all", "any", "total"] or args.category.lower() in ["all", "any", "total"]:
        print("Error: Calculation refused. This agent is restricted to per-ward and per-category analysis. Aggregation is not permitted.")
        sys.exit(1)

    try:
        data = load_dataset(args.input)
        results = compute_growth(data, args.ward, args.category, args.growth_type)
        
        if not results:
            print(f"No data found for Ward: {args.ward}, Category: {args.category}")
            return

        # Write results
        keys = results[0].keys()
        with open(args.output, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(results)
            
        print(f"Success: Analysis written to {args.output}")
        
    except Exception as e:
        print(f"Analysis Failed: {e}")

if __name__ == "__main__":
    main()

