import argparse
import csv
import sys
import os

def load_dataset(input_path):
    if not os.path.exists(input_path):
        print(f"Error: File not found {input_path}")
        sys.exit(1)
    
    data = []
    with open(input_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        required_cols = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
        if not required_cols.issubset(set(reader.fieldnames)):
            print(f"Error: Missing columns. Required: {required_cols}")
            sys.exit(1)
            
        for row in reader:
            data.append(row)
    return data

def compute_growth(ward_name, category_name, growth_type, dataset):
    # Filter data
    filtered = [r for r in dataset if r['ward'] == ward_name and r['category'] == category_name]
    
    # Sort by period
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    for i in range(len(filtered)):
        curr = filtered[i]
        period = curr['period']
        actual_curr_str = curr['actual_spend'].strip()
        notes = curr['notes'].strip()
        
        # Check for NULL
        if not actual_curr_str:
            results.append({
                'Ward': ward_name,
                'Category': category_name,
                'Period': period,
                'Actual Spend (₹ lakh)': 'NULL',
                'MoM Growth': f"NULL FLAG: {notes}"
            })
            continue

        actual_curr = float(actual_curr_str)
        
        if i == 0:
            growth_val = "n/a (First period)"
        else:
            prev = filtered[i-1]
            actual_prev_str = prev['actual_spend'].strip()
            
            if not actual_prev_str:
                growth_val = f"NULL FLAG: Cannot compute (Previous period was NULL)"
            else:
                actual_prev = float(actual_prev_str)
                if actual_prev == 0:
                    growth_val = "n/a (Prev spend is 0)"
                else:
                    diff = actual_curr - actual_prev
                    pct = (diff / actual_prev) * 100
                    sign = "+" if pct >= 0 else ""
                    formula = f"(({actual_curr} - {actual_prev}) / {actual_prev}) * 100"
                    growth_val = f"{sign}{pct:.1f}% [{formula}]"
        
        results.append({
            'Ward': ward_name,
            'Category': category_name,
            'Period': period,
            'Actual Spend (₹ lakh)': actual_curr,
            'MoM Growth': growth_val
        })
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Analyst")
    parser.add_argument("--input", required=True, help="Input CSV path")
    parser.add_argument("--ward", required=True, help="Ward name")
    parser.add_argument("--category", required=True, help="Category name")
    parser.add_argument("--growth-type", help="Growth type (MoM/YoY)")
    parser.add_argument("--output", default="growth_output.csv", help="Output CSV path")
    
    args = parser.parse_args()
    
    if not args.growth_type:
        print("Error: --growth-type not specified. Refusing to guess. Please choose MoM or YoY.")
        sys.exit(1)
    
    if args.growth_type.lower() != "mom":
        print(f"Error: Only MoM growth type is currently supported (Refuting {args.growth_type})")
        sys.exit(1)

    dataset = load_dataset(args.input)
    
    # Check if ward/category exist
    wards = {r['ward'] for r in dataset}
    categories = {r['category'] for r in dataset}
    
    if args.ward not in wards:
        print(f"Error: Ward '{args.ward}' not found in dataset.")
        sys.exit(1)
    if args.category not in categories:
        print(f"Error: Category '{args.category}' not found in dataset.")
        sys.exit(1)
        
    results = compute_growth(args.ward, args.category, args.growth_type.upper(), dataset)
    
    # Write output
    with open(args.output, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['Ward', 'Category', 'Period', 'Actual Spend (₹ lakh)', 'MoM Growth'])
        writer.writeheader()
        writer.writerows(results)
    
    print(f"Analysis complete. Results written to {args.output}")

if __name__ == "__main__":
    main()
