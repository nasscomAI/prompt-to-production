import argparse
import csv
import sys
from typing import List, Dict

def load_dataset(filepath: str) -> List[Dict[str, str]]:
    """Reads CSV, validates columns, reports null count and which rows."""
    expected_columns = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
    dataset = []
    null_rows = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames or not expected_columns.issubset(set(reader.fieldnames)):
                raise ValueError(f"CSV missing required columns. Expected: {expected_columns}")
            
            for row in reader:
                dataset.append(row)
                if not row['actual_spend'] or row['actual_spend'].strip().upper() == 'NULL':
                    null_rows.append(row)
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {filepath}")
    
    print(f"Dataset loaded. Total null 'actual_spend' values found: {len(null_rows)}")
    for row in null_rows:
        print(f"  - Flagged Null: {row['period']} | {row['ward']} | {row['category']} -> Reason: {row['notes']}")

    return dataset

def compute_growth(dataset: List[Dict[str, str]], ward: str, category: str, growth_type: str) -> List[Dict[str, str]]:
    """Computes growth metrics per period, flagging formulas and refusing to aggregate across multiple wards/categories."""
    if not growth_type:
        raise ValueError("Growth type not specified. System refuses to guess default growth metric.")
    
    if not ward or not category or ward.lower() == 'any' or category.lower() == 'any':
        raise ValueError("Aggregations across all wards or categories are not permitted. Please specify distinct --ward and --category.")
    
    filtered = [row for row in dataset if row['ward'] == ward and row['category'] == category]
            
    if not filtered:
        print(f"Warning: No data found for ward '{ward}' and category '{category}'.")
        return []
        
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    for i, row in enumerate(filtered):
        period = row['period']
        actual_str = row['actual_spend'].strip()
        notes = row.get('notes', '').strip()
        is_null = not actual_str or actual_str.upper() == 'NULL'
        
        res_row = {
            'Ward': row['ward'],
            'Category': row['category'],
            'Period': period,
            'Actual Spend (₹ lakh)': 'NULL' if is_null else actual_str,
            f'{growth_type} Growth': '',
            'Formula': ''
        }
        
        if is_null:
            res_row[f'{growth_type} Growth'] = f"NULL flagged (Reason: {notes})"
            res_row['Formula'] = "N/A"
            results.append(res_row)
            continue
            
        current_spend = float(actual_str)
        
        if growth_type.upper() == 'MOM':
            if i == 0:
                res_row[f'{growth_type} Growth'] = "N/A (first period)"
                res_row['Formula'] = "N/A"
            else:
                prev_actual_str = filtered[i-1]['actual_spend'].strip()
                prev_is_null = not prev_actual_str or prev_actual_str.upper() == 'NULL'
                
                if prev_is_null:
                    res_row[f'{growth_type} Growth'] = "Cannot compute (previous period was NULL)"
                    res_row['Formula'] = "N/A"
                else:
                    prev_spend = float(prev_actual_str)
                    if prev_spend == 0:
                        res_row[f'{growth_type} Growth'] = "N/A (div by zero)"
                        res_row['Formula'] = f"({current_spend} - 0) / 0 * 100"
                    else:
                        growth = (current_spend - prev_spend) / prev_spend * 100
                        sign = "+" if growth > 0 else "−" if growth < 0 else ""
                        abs_growth = abs(growth)
                        
                        suffix = f" ({notes})" if notes else ""
                        res_row[f'{growth_type} Growth'] = f"{sign}{abs_growth:.1f}%{suffix}"
                        res_row['Formula'] = f"({current_spend} - {prev_spend}) / {prev_spend} * 100"
        else:
            raise ValueError(f"Growth type '{growth_type}' is unsupported.")
             
        results.append(res_row)
        
    return results

def main():
    parser = argparse.ArgumentParser(description="Budget Analysis Agent")
    parser.add_argument('--input', required=True, help="Input CSV file path")
    parser.add_argument('--ward', help="Ward name (required to avoid aggregation)")
    parser.add_argument('--category', help="Category name (required to avoid aggregation)")
    parser.add_argument('--growth-type', help="Type of growth to compute (e.g., MoM)")
    parser.add_argument('--output', required=True, help="Output CSV file path")
    
    args = parser.parse_args()
    
    if not args.growth_type:
        print("Error: --growth-type must be specified. System refuses to guess.", file=sys.stderr)
        sys.exit(1)
         
    if not args.ward or args.ward.lower() in ("all", "any") or \
       not args.category or args.category.lower() in ("all", "any"):
        print("Error: System refuses to aggregate across wards or categories. Explicit --ward and --category required.", file=sys.stderr)
        sys.exit(1)

    try:
        dataset = load_dataset(args.input)
        results = compute_growth(dataset, args.ward, args.category, args.growth_type)
        
        if not results:
            print("No output generated.")
            sys.exit(0)
             
        with open(args.output, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
            
        print(f"Success. Analysis written to {args.output}")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
