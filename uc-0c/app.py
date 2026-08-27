"""
UC-0C app.py — Solution.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import sys
import csv

def load_dataset(input_file):
    dataset = []
    try:
        with open(input_file, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            # validate required cols
            required_cols = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
            for col in required_cols:
                if col not in reader.fieldnames:
                    print(f"Error: Missing required column {col}")
                    sys.exit(1)
            
            for row in reader:
                dataset.append(row)
    except Exception as e:
        print(f"Error reading {input_file}: {e}")
        sys.exit(1)
        
    # explicitly report nulls
    null_rows = [row for row in dataset if not row['actual_spend'].strip()]
    print(f"[load_dataset] Found {len(null_rows)} explicitly null 'actual_spend' rows.")
    for row in null_rows:
        note = row['notes'] if row['notes'].strip() else 'Missing reason'
        print(f"  - NULL found in {row['period']} for '{row['ward']}' / '{row['category']}'. Note: {note}")
        
    return dataset

def compute_growth(dataset, target_ward, target_category, growth_type):
    # Enforce rule: never aggregate.
    if target_ward == "All" or target_category == "All" or not target_ward or not target_category:
        print("Refusal: Never aggregate across wards or categories unless explicitly instructed.", file=sys.stderr)
        sys.exit(1)
        
    filtered = [row for row in dataset if row['ward'] == target_ward and row['category'] == target_category]
    filtered.sort(key=lambda x: x['period'])
    
    if not filtered:
        print("Warning: No data found for specified ward and category.")
        return []

    results = []
    
    for i, row in enumerate(filtered):
        period = row['period']
        actual_str = row['actual_spend'].strip()
        notes = row['notes'].strip()
        
        if not actual_str:
            results.append({
                'Ward': target_ward,
                'Category': target_category,
                'Period': period,
                'Actual Spend (₹ lakh)': 'NULL',
                'MoM Growth': "Must be flagged — not computed",
                'Formula': f"Flagged null: {notes}"
            })
            continue

        actual = float(actual_str)
        formula_used = 'n/a'
        growth_str = 'n/a'
        
        if growth_type == 'MoM':
            if i > 0:
                prev_row = filtered[i-1]
                prev_actual_str = prev_row['actual_spend'].strip()
                
                if prev_actual_str:
                    prev_actual = float(prev_actual_str)
                    growth = (actual - prev_actual) / prev_actual
                    growth_pct = growth * 100
                    sign = "+" if growth > 0 else "−" if growth < 0 else ""
                    growth_str = f"{sign}{abs(growth_pct):.1f}%"
                    formula_used = f"({actual} - {prev_actual}) / {prev_actual}"
                    if notes:
                        growth_str += f" ({notes})"
                else:
                    growth_str = 'n/a'
                    formula_used = 'previous actual is null'
                    
        elif growth_type == 'YoY':
            growth_str = 'n/a'
            formula_used = 'No previous year data'

        results.append({
            'Ward': target_ward,
            'Category': target_category,
            'Period': period,
            'Actual Spend (₹ lakh)': actual,
            'MoM Growth': growth_str,
            'Formula': formula_used
        })
    
    return results

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--ward', required=True)
    parser.add_argument('--category', required=True)
    parser.add_argument('--growth-type', required=False) # Not required so we can reject it if missing
    parser.add_argument('--output', required=True)
    args = parser.parse_args()

    if not args.growth_type:
        print("Refusal: --growth-type not specified. Please ask, never guess.", file=sys.stderr)
        sys.exit(1)

    dataset = load_dataset(args.input)
    res_list = compute_growth(dataset, args.ward, args.category, args.growth_type)
    
    if res_list:
        with open(args.output, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=res_list[0].keys())
            writer.writeheader()
            writer.writerows(res_list)
        print(f"Output saved to {args.output}")

if __name__ == "__main__":
    main()
