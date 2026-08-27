import argparse
import csv
import sys

def load_dataset(input_path):
    rows = []
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows

def compute_growth(rows, ward, category, growth_type):
    if ward == "Any" or category == "Any":
        print("Error: Aggregation across wards or categories is not permitted.")
        sys.exit(1)
        
    filtered = [r for r in rows if r['ward'] == ward and r['category'] == category]
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    for i, row in enumerate(filtered):
        if not row['actual_spend']:
            results.append({
                'Period': row['period'],
                'Ward': row['ward'],
                'Category': row['category'],
                'Actual Spend (₹ lakh)': 'NULL',
                'MoM Growth': f"Must be flagged — not computed. Notes: {row['notes']}",
                'Formula': 'N/A'
            })
            continue
            
        current = float(row['actual_spend'])
        if i == 0 or not filtered[i-1]['actual_spend']:
            growth_str = f"n/a ({row['notes']})" if row.get('notes') else "n/a (no prior data)"
            formula_str = "N/A"
        else:
            prev = float(filtered[i-1]['actual_spend'])
            growth = ((current - prev)/prev) * 100
            sign = "+" if growth > 0 else ""
            growth_str = f"{sign}{growth:.1f}% ({row.get('notes', 'baseline')})"
            formula_str = f"(({current} - {prev}) / {prev}) * 100"
            
        results.append({
            'Period': row['period'],
            'Ward': row['ward'],
            'Category': row['category'],
            'Actual Spend (₹ lakh)': current,
            'MoM Growth': growth_str.strip(),
            'Formula': formula_str
        })
    return results

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=False, default=None)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    
    if not args.growth_type:
        print("Refusal: --growth-type not specified. Please request explicit computation (e.g. MoM or YoY).")
        sys.exit(1)
        
    rows = load_dataset(args.input)
    results = compute_growth(rows, args.ward, args.category, args.growth_type)
    
    if len(results) == 0:
        print("No valid matches found.")
        sys.exit(0)
        
    with open(args.output, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
        
    print(f"Results written to {args.output}")

if __name__ == "__main__":
    main()
