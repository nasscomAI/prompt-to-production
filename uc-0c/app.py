import argparse
import csv

def compute_growth(input_file, target_ward, target_category, growth_type, output_file):
    if not growth_type:
        print("Error: --growth-type not specified. Refusing to guess.")
        return
        
    results = []
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['ward'] == target_ward and row['category'] == target_category:
                results.append(row)
                
    results.sort(key=lambda x: x['period'])
    
    output_rows = []
    prev_val = None
    
    for row in results:
        spend_str = row['actual_spend'].strip()
        if not spend_str:
            output_rows.append({
                'period': row['period'],
                'ward': row['ward'],
                'category': row['category'],
                'actual_spend': 'NULL',
                'growth': f"Flagged Null: {row.get('notes', '')}",
                'formula': 'N/A'
            })
            prev_val = None
            continue
            
        spend = float(spend_str)
        if prev_val is not None and growth_type == 'MoM':
            # Note for MoM formula
            formula = f"({spend} - {prev_val}) / {prev_val} * 100"
            growth = ((spend - prev_val) / prev_val) * 100
            growth_str = f"{growth:+.1f}%"
        else:
            growth_str = "no previous period to calculate"
            formula = "N/A"
            
        output_rows.append({
            'period': row['period'],
            'ward': row['ward'],
            'category': row['category'],
            'actual_spend': spend,
            'growth': growth_str,
            'formula': formula
        })
        prev_val = spend
        
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['period', 'ward', 'category', 'actual_spend', 'growth', 'formula'])
        writer.writeheader()
        writer.writerows(output_rows)
        
    print(f"Results written to {output_file}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--ward", required=False)
    parser.add_argument("--category", required=False)
    parser.add_argument("--growth-type", required=False)
    args = parser.parse_args()
    
    if args.ward == "All" or args.category == "All":
        print("Error: Refusing to aggregate across wards or categories.")
        return
        
    if not args.ward or not args.category:
        print("Error: Must specify --ward and --category individually.")
        return
        
    compute_growth(args.input, args.ward, args.category, args.growth_type, args.output)

if __name__ == "__main__":
    main()
