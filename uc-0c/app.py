import argparse
import csv
import sys
import os

def load_dataset(filepath):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
        
    data = []
    with open(filepath, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        
        required_columns = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
        for col in required_columns:
            if col not in headers:
                raise ValueError(f"Missing required column: {col}")
                
        for row in reader:
            data.append(row)
            
    # Rule: Flag every null row before computing — report null reason from the notes column
    null_rows = [row for row in data if not row['actual_spend'] or row['actual_spend'].strip().upper() == 'NULL']
    if null_rows:
        print(f"Reporting {len(null_rows)} null 'actual_spend' values before computing:")
        for row in null_rows:
            reason = row.get('notes', 'No reason provided')
            print(f" - Period: {row['period']} | Ward: {row['ward']} | Category: {row['category']} | Reason: {reason}")
            
    return data

def compute_growth(data, ward, category, growth_type):
    # Rule: If --growth-type is not specified — refuse and ask, never guess
    if not growth_type:
        raise ValueError("Refused: --growth-type is not specified. Will not guess.")
        
    # Rule: Never aggregate across wards or categories unless explicitly instructed — refuse if asked
    if not ward or not category or str(ward).lower() in ['all', 'any'] or str(category).lower() in ['all', 'any'] or ',' in str(ward) or ',' in str(category):
        raise ValueError("Refused: Cannot aggregate across wards or categories. Please specify a single ward and category.")

    filtered_data = [row for row in data if row['ward'] == ward and row['category'] == category]
    
    if not filtered_data:
        print(f"Warning: No data found for ward '{ward}' and category '{category}'.")
        return []
        
    filtered_data.sort(key=lambda x: x['period'])
    
    results = []
    shift_amount = 12 if growth_type.upper() == 'YOY' else 1
        
    for i in range(len(filtered_data)):
        row = filtered_data[i]
        period = row['period']
        actual_spend_raw = row['actual_spend']
        notes = row.get('notes', '')
        
        is_null = not actual_spend_raw or actual_spend_raw.strip().upper() == 'NULL'
        
        if is_null:
            actual_spend_val = None
            # Flag nulls explicitly
            growth_str = "Must be flagged — not computed"
            if notes and notes.strip():
                growth_str += f" ({notes.strip()})"
            formula_str = "N/A"
        else:
            try:
                actual_spend_val = float(actual_spend_raw)
            except ValueError:
                actual_spend_val = None
                growth_str = "Must be flagged — not computed (Invalid value)"
                formula_str = "N/A"
                is_null = True

        if not is_null:
            if i >= shift_amount:
                prev_row = filtered_data[i - shift_amount]
                prev_spend_raw = prev_row['actual_spend']
                prev_is_null = not prev_spend_raw or prev_spend_raw.strip().upper() == 'NULL'
                
                if prev_is_null:
                    growth_str = "Cannot compute (previous period is NULL)"
                    formula_str = f"({actual_spend_val} - NULL) / NULL"
                else:
                    try:
                        prev_spend_val = float(prev_spend_raw)
                        if prev_spend_val == 0:
                            growth_str = "Cannot compute (previous period is 0)"
                            formula_str = f"({actual_spend_val} - 0) / 0"
                        else:
                            growth = (actual_spend_val - prev_spend_val) / prev_spend_val
                            growth_pct = growth * 100
                            
                            sign = "+" if growth > 0 else "−" if growth < 0 else ""
                            growth_pct_abs = abs(growth_pct)
                            note_str = f" ({notes})" if notes and notes.strip() else ""
                            growth_str = f"{sign}{growth_pct_abs:.1f}%{note_str}"
                            # Rule: Show formula used in every output row alongside the result
                            formula_str = f"({actual_spend_val} - {prev_spend_val}) / {prev_spend_val}"
                    except ValueError:
                        growth_str = "Cannot compute (previous period invalid)"
                        formula_str = f"({actual_spend_val} - INVALID) / INVALID"
            else:
                growth_str = "n/a"
                formula_str = "n/a"
                
        results.append({
            'Ward': ward,
            'Category': category,
            'Period': period,
            'Actual Spend': actual_spend_val if not is_null else 'NULL',
            f'{growth_type} Growth': growth_str,
            'Formula Used': formula_str
        })
        
    return results

def main():
    parser = argparse.ArgumentParser(description="Calculate growth from budget data.")
    parser.add_argument("--input", required=True, help="Input CSV file")
    parser.add_argument("--ward", required=False, help="Ward name")
    parser.add_argument("--category", required=False, help="Category name")
    parser.add_argument("--growth-type", required=False, help="Type of growth to compute (e.g., MoM)")
    parser.add_argument("--output", required=True, help="Output CSV file")
    
    args = parser.parse_args()
    
    # Catching args missing before running processing
    if not args.growth_type:
        print("Refused: --growth-type not specified. Please specify the growth type, I will not guess.")
        sys.exit(1)
        
    if not args.ward or not args.category:
        print("Refused: Ward and Category must be specified to prevent aggregation.")
        sys.exit(1)
        
    try:
        data = load_dataset(args.input)
        results = compute_growth(data, args.ward, args.category, args.growth_type)
        if results:
            os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
            with open(args.output, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=results[0].keys())
                writer.writeheader()
                writer.writerows(results)
            print(f"Output saved to {args.output}")
    except ValueError as ve:
        print(f"Error: {ve}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
