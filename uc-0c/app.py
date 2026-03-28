import argparse
import csv

def compute_growth(input_file, output_file, target_ward, target_category, growth_type):
    if growth_type.lower() != 'mom':
        # Rule 4 & 1
        raise ValueError(f"Unsupported or missing growth-type explicitly allowed: {growth_type}. Only MoM is supported in this context natively.")
        
    rows = []
    # Load dataset
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['ward'] == target_ward and row['category'] == target_category:
                rows.append(row)
                
    if not rows:
        print(f"Warning: No data found for Ward: '{target_ward}' and Category: '{target_category}'")
    
    # Sort chronologically
    rows.sort(key=lambda x: x['period'])
    
    output_rows = []
    prev_spend = None
    
    for row in rows:
        period = row['period']
        # Rule 2: Note extraction
        notes = row.get('notes', '')
        raw_spend = row['actual_spend'].strip() if row.get('actual_spend') else ''
        
        computed_growth = ''
        formula_used = ''
        
        if not raw_spend:
            # Null detected natively without silent computation
            computed_growth = 'NULL'
            formula_used = 'N/A'
            notes = f"Flagged NULL: {notes}" if notes else "Flagged NULL"
            prev_spend = None  # Reset tracking
        else:
            current_spend = float(raw_spend)
            if prev_spend is not None:
                # Rule 3: Showing the formula
                growth_val = ((current_spend - prev_spend) / prev_spend) * 100
                prefix = "+" if growth_val >= 0 else ""
                computed_growth = f"{prefix}{growth_val:.1f}%"
                formula_used = f"({current_spend} - {prev_spend}) / {prev_spend}"
            else:
                computed_growth = 'n/a'
                formula_used = 'No previous month data'
                
            prev_spend = current_spend
            
        output_rows.append({
            'period': period,
            'ward': target_ward,
            'category': target_category,
            'actual_spend': raw_spend if raw_spend else 'NULL',
            'growth': computed_growth,
            'formula': formula_used,
            'notes': notes
        })
        
    # Write output
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['period', 'ward', 'category', 'actual_spend', 'growth', 'formula', 'notes'])
        writer.writeheader()
        writer.writerows(output_rows)
        
    print(f"Growth calculation complete. Saved to {output_file}")


def main():
    parser = argparse.ArgumentParser(description="UC-0C Financial Growth Calculator", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Must specify exactly one ward (e.g. 'Ward 1 - Kasba')")
    parser.add_argument("--category", required=True, help="Must specify exactly one category")
    parser.add_argument("--growth-type", required=True, help="Must be explicit (e.g. MoM)")
    parser.add_argument("--output", required=True, help="Output CSV path")

    # If any required arg is missing, argparse will refuse and exit natively, fulfilling rule 1 and 4!
    args = parser.parse_args()
    
    compute_growth(args.input, args.output, args.ward, args.category, args.growth_type)

if __name__ == "__main__":
    main()
