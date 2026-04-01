import argparse
import csv
import sys

def load_dataset(input_path):
    rows = []
    nulls = []
    
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
            if not row['actual_spend'].strip():
                nulls.append(row)
    
    # Enforcement: Flag every null row before computing
    print(f"Data Load: Found {len(nulls)} deliberate null rows in 'actual_spend'.")
    for n in nulls:
        # report reason from notes column
        print(f"  -> Flagged Null: {n['period']} | {n['ward']} | {n['category']} | Note: {n['notes']}")
        
    return rows

def compute_growth(rows, ward, category, growth_type, output_path):
    # Enforcement: Refuse aggregation across wards/categories silently
    if not ward or not category:
        print("\nERROR [Refusal]: Cannot aggregate across multiple wards/categories silently. You must specify --ward and --category.")
        sys.exit(1)
        
    # Enforcement: Refuse if growth-type missing
    if not growth_type:
        print("\nERROR [Refusal]: --growth-type not specified. Refusing to guess the formula.")
        sys.exit(1)
        
    if growth_type != "MoM":
        print(f"\nERROR: Only MoM is supported in this scoped execution. Received {growth_type}")
        sys.exit(1)
        
    filtered = [r for r in rows if r['ward'] == ward and r['category'] == category]
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    
    for i in range(len(filtered)):
        curr_row = filtered[i]
        period = curr_row['period']
        actual_spend = curr_row['actual_spend'].strip()
        
        formula = ""
        mom_growth = ""
        
        if not actual_spend:
            mom_growth = f"NULL ({curr_row['notes']})"
            formula = "Flagged: Missing data"
        else:
            curr_val = float(actual_spend)
            if i == 0:
                mom_growth = "n/a"
                formula = "No previous month"
            else:
                prev_spend = filtered[i-1]['actual_spend'].strip()
                if not prev_spend:
                    mom_growth = "n/a (Prev missing)"
                    formula = "Prev missing"
                else:
                    prev_val = float(prev_spend)
                    if prev_val == 0:
                        mom_growth = "n/a"
                        formula = f"({curr_val} - 0) / 0"
                    else:
                        growth = ((curr_val - prev_val) / prev_val) * 100
                        mom_growth = f"{growth:+.1f}%"
                        # Enforcement: Show formula used
                        formula = f"(({curr_val} - {prev_val}) / {prev_val}) * 100"
                        
        results.append({
            'ward': ward,
            'category': category,
            'period': period,
            'actual_spend': actual_spend if actual_spend else "NULL",
            'mom_growth': mom_growth,
            'formula_used': formula
        })
        
    if not results:
        print("\nWarning: No data found for the specified ward/category combination.")
        sys.exit(1)
        
    # Write output properly formatted per requirement
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['ward', 'category', 'period', 'actual_spend', 'mom_growth', 'formula_used'])
        writer.writeheader()
        writer.writerows(results)
        
    print(f"\nSuccess! Scoped output calculation written to {output_path}")

def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    # Kept required=False deliberately to test refusal logic if omitted
    parser.add_argument("--ward", required=False)
    parser.add_argument("--category", required=False)
    parser.add_argument("--growth-type", required=False) 
    
    args = parser.parse_args()
    
    rows = load_dataset(args.input)
    compute_growth(rows, args.ward, args.category, args.growth_type, args.output)

if __name__ == "__main__":
    main()
