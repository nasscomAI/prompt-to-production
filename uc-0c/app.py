import argparse
import csv
import sys

def load_dataset(input_path, target_ward, target_category):
    if not target_ward or not target_category:
        print("ERROR: Missing ward or category filter. Never aggregate across wards or categories unless explicitly instructed!")
        sys.exit(1)
        
    data = []
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['ward'] == target_ward and row['category'] == target_category:
                data.append(row)
                
    data.sort(key=lambda x: x['period'])
    return data

def compute_growth(data, growth_type):
    if not growth_type:
        print("ERROR: --growth-type not specified. Refusing to guess formula.")
        sys.exit(1)
        
    if growth_type.upper() != "MOM":
        print(f"ERROR: unsupported growth type {growth_type}")
        sys.exit(1)
        
    results = []
    prev_spend = None
    
    for row in data:
        spend_str = row.get('actual_spend', '').strip()
        period = row['period']
        notes = row.get('notes', '').strip()
        
        base_formula = "(Current - Previous) / Previous"
        
        if not spend_str:
            # FLAG explicitly and report notes as null reason
            results.append({
                "period": period,
                "ward": row['ward'],
                "category": row['category'],
                "actual_spend": "NULL",
                "growth": "FLAGGED_NULL",
                "formula": "Not computed (missing data)",
                "notes": notes if notes else "Data missing"
            })
            prev_spend = None
            continue
            
        try:
            current_spend = float(spend_str)
        except ValueError:
            current_spend = 0.0
            
        if prev_spend is None:
            growth_val = "N/A"
            formula_used = "N/A (First period or missing previous)"
        else:
            if prev_spend == 0:
                growth_val = "N/A"
                formula_used = "N/A (Div by zero)"
            else:
                growth = (current_spend - prev_spend) / prev_spend
                growth_val = f"{growth * 100:+.1f}%"
                formula_used = f"({current_spend} - {prev_spend}) / {prev_spend} = {base_formula}"
                
        results.append({
            "period": period,
            "ward": row['ward'],
            "category": row['category'],
            "actual_spend": current_spend,
            "growth": growth_val,
            "formula": formula_used,
            "notes": notes
        })
        
        prev_spend = current_spend
        
    return results

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=False)
    parser.add_argument("--category", required=False)
    parser.add_argument("--growth-type", required=False)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    
    data = load_dataset(args.input, args.ward, args.category)
    results = compute_growth(data, args.growth_type)
    
    if not results:
        print("No data found for this ward and category combination.")
        sys.exit(0)
        
    keys = ["period", "ward", "category", "actual_spend", "growth", "formula", "notes"]
    with open(args.output, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(results)
        
    print(f"Done. Output written to {args.output}")

if __name__ == "__main__":
    main()
