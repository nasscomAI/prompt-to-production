import argparse
import csv
import sys

def load_dataset(file_path):
    dataset = []
    null_report = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            required_cols = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
            
            if not all(col in reader.fieldnames for col in required_cols):
                print(f"Error: Missing required columns. Found: {reader.fieldnames}")
                sys.exit(1)
            
            for row in reader:
                dataset.append(row)
                actual_val = row.get('actual_spend', '').strip()
                if not actual_val:
                    null_report.append({
                        'period': row['period'],
                        'ward': row['ward'],
                        'category': row['category'],
                        'notes': row.get('notes', 'No reason provided')
                    })
    except Exception as e:
        print(f"Error loading dataset {file_path}: {e}")
        sys.exit(1)
        
    print(f"Dataset successfully loaded. Total rows: {len(dataset)}")
    
    # Rule 2: Flag every null row before computing — report null reason from the notes column
    if null_report:
        print(f"\n[FLAG] Found {len(null_report)} rows with NULL actual_spend:")
        for r in null_report:
            print(f"  - {r['period']} | {r['ward']} | {r['category']} | Reason: {r['notes']}")
        print("\nThese rows will not be computed.\n")
    else:
        print("No null actual_spend rows found.\n")
        
    return dataset


def compute_growth(dataset, ward, category, growth_type):
    # Rule 4: If --growth-type not specified — refuse and ask, never guess
    if not growth_type:
        print("[REFUSAL] --growth-type was not specified. I cannot assume a formula. Please specify (e.g. MoM, YoY).")
        sys.exit(1)
        
    # Rule 1: Never aggregate across wards or categories unless explicitly instructed — refuse if asked
    if ward.lower() in ['all', 'any'] or category.lower() in ['all', 'any']:
        print("[REFUSAL] I am instructed never to aggregate across wards or categories. Please specify a single ward and category.")
        sys.exit(1)
        
    filtered = [r for r in dataset if r['ward'] == ward and r['category'] == category]
    
    if not filtered:
        print(f"No data found for Ward: '{ward}', Category: '{category}'.")
        sys.exit(1)
        
    # Sort chronologically
    filtered.sort(key=lambda x: x['period'])
    
    growth_table = []
    
    for i, row in enumerate(filtered):
        period = row['period']
        notes = row.get('notes', '').strip()
        actual_str = row.get('actual_spend', '').strip()
        
        notes_append = f" ({notes})" if notes else ""
        
        if not actual_str:
            growth_table.append({
                'ward': ward,
                'category': category,
                'period': period,
                'actual_spend': 'NULL',
                'growth': 'NULL',
                'formula': 'Cannot compute: actual_spend is NULL'
            })
            continue
            
        actual_spend = float(actual_str)
        
        if growth_type.lower() == 'mom':
            if i == 0:
                growth_table.append({
                    'ward': ward,
                    'category': category,
                    'period': period,
                    'actual_spend': actual_spend,
                    'growth': 'n/a',
                    'formula': 'First period, no previous month to compare'
                })
            else:
                prev_str = filtered[i-1].get('actual_spend', '').strip()
                if not prev_str:
                    growth_table.append({
                        'ward': ward,
                        'category': category,
                        'period': period,
                        'actual_spend': actual_spend,
                        'growth': 'NULL',
                        'formula': f"Cannot compute: previous month ({filtered[i-1]['period']}) is NULL"
                    })
                else:
                    prev_spend = float(prev_str)
                    if prev_spend == 0:
                        growth_table.append({
                            'ward': ward,
                            'category': category,
                            'period': period,
                            'actual_spend': actual_spend,
                            'growth': 'n/a',
                            'formula': 'Division by zero (previous spend was 0)'
                        })
                    else:
                        growth_pct = ((actual_spend - prev_spend) / prev_spend) * 100
                        sign = "+" if growth_pct > 0 else ""
                        growth_str = f"{sign}{growth_pct:.1f}%{notes_append}"
                        
                        # Rule 3: Show formula used in every output row alongside the result
                        formula_str = f"(({actual_spend} - {prev_spend}) / {prev_spend}) * 100"
                        
                        growth_table.append({
                            'ward': ward,
                            'category': category,
                            'period': period,
                            'actual_spend': actual_spend,
                            'growth': growth_str,
                            'formula': formula_str
                        })
        else:
            print(f"[REFUSAL] Unknown growth type '{growth_type}'. Only 'MoM' is supported in this implementation.")
            sys.exit(1)
            
    return growth_table


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Computer")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Specific ward name")
    parser.add_argument("--category", required=True, help="Specific category name")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    
    # Intentionally optional to trigger Rule 4 refusal
    parser.add_argument("--growth-type", help="Type of growth calculation (e.g., MoM)")
    
    args = parser.parse_args()
    
    dataset = load_dataset(args.input)
    growth_table = compute_growth(dataset, args.ward, args.category, args.growth_type)
    
    try:
        with open(args.output, 'w', encoding='utf-8', newline='') as f:
            fieldnames = ['ward', 'category', 'period', 'actual_spend', 'growth', 'formula']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(growth_table)
            
        print(f"Success! Growth table written to {args.output}")
    except Exception as e:
        print(f"Error writing output file: {e}")

if __name__ == "__main__":
    main()
