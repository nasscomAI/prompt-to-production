import argparse
import csv
import sys

def load_dataset(input_path):
    dataset = []
    null_rows = []
    
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        required_cols = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
        if not required_cols.issubset(set(reader.fieldnames or [])):
            raise ValueError(f"Missing required columns. Expected at least: {required_cols}")
        
        for row in reader:
            val = row.get('actual_spend', '').strip()
            # Deliberate null condition
            if val == '' or val.lower() == 'null':
                null_rows.append(row)
            dataset.append(row)
            
    print(f"Dataset securely loaded. Total rows: {len(dataset)}")
    if null_rows:
        print(f"FLAGGED: {len(null_rows)} explicitly null 'actual_spend' rows found!")
        for r in null_rows:
            note = r.get('notes', 'N/A')
            print(f"  - Period: {r['period']} | Ward: {r['ward']} | Category: {r['category']} | Reason: {note}")
            
    return dataset

def compute_growth(dataset, target_ward, target_category, growth_type):
    # Normalize inputs to avoid dash mismatch (- vs –)
    def normalize(text):
        return text.replace('–', '-').replace('—', '-').lower().strip()
        
    t_ward_norm = normalize(target_ward)
    t_cat_norm = normalize(target_category)

    if t_ward_norm in ('any', 'all') or t_cat_norm in ('any', 'all') or ',' in target_ward or ',' in target_category:
        raise ValueError("Aggregation across wards or categories is explicitly forbidden by agent rules. Refusing.")

    if not growth_type:
        raise ValueError("Growth type not specified. Never guess.")

    subset = [r for r in dataset if normalize(r.get('ward', '')) == t_ward_norm and normalize(r.get('category', '')) == t_cat_norm]
    if not subset:
        print("Warning: No matching data found for the provided ward and category.")
        return []
        
    subset.sort(key=lambda x: x.get('period', ''))
    
    results = []
    for i, row in enumerate(subset):
        period = row.get('period')
        current_spend_str = row.get('actual_spend', '').strip()
        
        is_current_null = (current_spend_str == '' or current_spend_str.lower() == 'null')
        current_spend = None if is_current_null else float(current_spend_str)
        
        note = row.get('notes', '').strip()
        note_str = f" ({note})" if note else ""

        growth_val = "NULL"
        formula = "NULL (Cannot compute)"
        
        if is_current_null:
            growth_val = "NULL"
            formula = f"NULL (Row is null. Reason: {note})"
        else:
            if growth_type.lower() == 'mom':
                if i == 0:
                    growth_val = "n/a"
                    formula = "n/a (First period)"
                else:
                    prev_row = subset[i-1]
                    prev_spend_str = prev_row.get('actual_spend', '').strip()
                    is_prev_null = (prev_spend_str == '' or prev_spend_str.lower() == 'null')
                    
                    if is_prev_null:
                        growth_val = "n/a"
                        formula = f"n/a (Previous period {prev_row.get('period')} was null)"
                    else:
                        prev_spend = float(prev_spend_str)
                        if prev_spend == 0:
                            growth_val = "n/a"
                            formula = f"({current_spend} - 0) / 0"
                        else:
                            calc = (current_spend - prev_spend) / prev_spend
                            growth_val = f"{calc:+.1%}"
                            formula = f"({current_spend} - {prev_spend}) / {prev_spend}"
                            
            else:
                raise ValueError(f"Unknown growth-type: {growth_type}. Refusing to compute.")

        results.append({
            'Ward': row.get('ward'),
            'Category': row.get('category'),
            'Period': period,
            'Actual Spend (\u20b9 lakh)': current_spend_str if not is_current_null else 'NULL',
            f'{growth_type} Growth': f"{growth_val}{note_str} [Formula: {formula}]"
        })
        
    return results

def main():
    parser = argparse.ArgumentParser(description="Budget Growth Calculation Agent")
    parser.add_argument("--input", required=True, help="Input CSV file path")
    parser.add_argument("--ward", required=True, help="Target ward")
    parser.add_argument("--category", required=True, help="Target category")
    parser.add_argument("--growth-type", required=False, help="Type of growth to compute (e.g., MoM)")
    parser.add_argument("--output", required=True, help="Output CSV file path")
    
    if '--growth-type' not in sys.argv:
        print("ERROR: --growth-type not specified. Refusing to guess. Please provide a growth type (e.g., MoM).", file=sys.stderr)
        sys.exit(1)
        
    args = parser.parse_args()
        
    try:
        dataset = load_dataset(args.input)
        results = compute_growth(dataset, args.ward, args.category, args.growth_type)
        
        if results:
            with open(args.output, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=results[0].keys())
                writer.writeheader()
                writer.writerows(results)
            print(f"Results written to {args.output}")
            
    except Exception as e:
        print(f"ERROR: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
