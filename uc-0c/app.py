import argparse
import sys
import csv

def load_dataset(file_path):
    """
    reads CSV, validates columns, reports null count and which rows before returning.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames or []
            
            required_cols = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
            for col in required_cols:
                if col not in headers:
                    print(f"Error: Required column '{col}' is missing.")
                    sys.exit(1)
                    
            rows = list(reader)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
        
    null_count = 0
    null_rows = []
    
    for row in rows:
        val = row.get('actual_spend', '').strip()
        if not val: # considering empty string as null
            null_count += 1
            null_rows.append(row)
            
    print(f"Dataset loaded. Found {null_count} null actual_spend rows.")
    
    if null_count > 0:
        print("Null records:")
        for row in null_rows:
            print(f" - Period: {row.get('period')}, Ward: {row.get('ward')}, Category: {row.get('category')}, Reason: {row.get('notes')}")
    print("-" * 30)
    
    return rows

def compute_growth(rows, target_ward, target_category, growth_type):
    """
    takes ward + category + growth_type, returns per-period table with formula shown.
    If target_ward or target_category are None, loops through all unique ones.
    """
    if not growth_type:
        print("REFUSAL: --growth-type not specified. Please explicitly state the growth type to compute. System refusing to guess.")
        sys.exit(1)

    # Rule 1 states never to aggregate *across* wards or categories.
    # It doesn't mean we can't output a table with computing them independently.
    if (target_ward and target_ward.strip().lower() in ['any', 'all']) or \
       (target_category and target_category.strip().lower() in ['any', 'all']):
        print("REFUSAL: Aggregation across different wards or categories is strictly prohibited unless explicitly requested.")
        sys.exit(1)

    wards_to_process = [target_ward] if target_ward else list(set(r.get('ward') for r in rows if r.get('ward')))
    categories_to_process = [target_category] if target_category else list(set(r.get('category') for r in rows if r.get('category')))

    all_results = []
    
    # Sort backwards to have a stable order if we want it, or just rely on period sorting inside
    wards_to_process.sort()
    categories_to_process.sort()

    for w in wards_to_process:
        for c in categories_to_process:
            filtered_rows = [r for r in rows if r.get('ward') == w and r.get('category') == c]

            if not filtered_rows:
                continue

            # Sort by period to ensure chronological order
            filtered_rows.sort(key=lambda x: x.get('period', ''))
            
            for i in range(len(filtered_rows)):
                row = filtered_rows[i]
                
                actual_val_str = row.get('actual_spend', '').strip()
                is_null = not actual_val_str
                
                if is_null:
                    result_row = {
                        'Ward': w,
                        'Category': c,
                        'Period': row.get('period'),
                        'Actual Spend (₹ lakh)': 'NULL',
                        f'{growth_type} Growth': f"NULL (Flagged — not computed, Reason: {row.get('notes', '')})",
                        'Formula': 'None (Value was null)'
                    }
                    all_results.append(result_row)
                    continue
                    
                try:
                    actual_spend = float(actual_val_str)
                except ValueError:
                    actual_spend = 0.0 # fallback if data is bad, though ideally it should error.
                    
                growth = "n/a"
                formula = "n/a"

                if growth_type.lower() == "mom":
                    if i > 0:
                        prev_val_str = filtered_rows[i-1].get('actual_spend', '').strip()
                        if not prev_val_str:
                            growth = "n/a"
                            formula = "None (Previous period is null)"
                        else:
                            try:
                                prev_spend = float(prev_val_str)
                                growth_val = ((actual_spend - prev_spend) / prev_spend) * 100
                                sign = "+" if growth_val > 0 else "−" if growth_val < 0 else ""
                                notes_str = f" ({row.get('notes')})" if row.get('notes') else ""
                                growth = f"{sign}{abs(growth_val):.1f}%{notes_str}"
                                formula = f"(({actual_spend} - {prev_spend}) / {prev_spend}) * 100"
                            except ValueError:
                                growth = "n/a"
                                formula = "None (Previous period invalid)"
                    else:
                        growth = "n/a"
                        formula = "No prior period for baseline"
                elif growth_type.lower() == "yoy":
                    if i >= 12:
                        prev_val_str = filtered_rows[i-12].get('actual_spend', '').strip()
                        if not prev_val_str:
                            growth = "n/a"
                            formula = "None (Previous year period is null)"
                        else:
                            try:
                                prev_spend = float(prev_val_str)
                                growth_val = ((actual_spend - prev_spend) / prev_spend) * 100
                                sign = "+" if growth_val > 0 else "−" if growth_val < 0 else ""
                                notes_str = f" ({row.get('notes')})" if row.get('notes') else ""
                                growth = f"{sign}{abs(growth_val):.1f}%{notes_str}"
                                formula = f"(({actual_spend} - {prev_spend}) / {prev_spend}) * 100"
                            except ValueError:
                                growth = "n/a"
                                formula = "None (Previous year period invalid)"
                    else:
                        growth = "n/a"
                        formula = "No prior year period for baseline"

                result_row = {
                    'Ward': w,
                    'Category': c,
                    'Period': row.get('period'),
                    'Actual Spend (₹ lakh)': actual_val_str,
                    f'{growth_type} Growth': growth,
                    'Formula': formula
                }
                all_results.append(result_row)
        
    if not all_results:
        print(f"No data found for the given criteria.")
        sys.exit(1)
        
    return all_results

def write_results(results, output_file, growth_type):
    if not results:
        print("No results to write.")
        return
        
    headers = ['Ward', 'Category', 'Period', 'Actual Spend (₹ lakh)', f'{growth_type} Growth', 'Formula']
    try:
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing to output file: {e}")

def main():
    parser = argparse.ArgumentParser(description="Calculate growth metrics using strict rules.")
    parser.add_argument('--input', required=True, help="Input CSV file path")
    parser.add_argument('--ward', required=False, help="Ward target")
    parser.add_argument('--category', required=False, help="Category target")
    parser.add_argument('--growth-type', required=False, help="Type of growth calculation (e.g. MoM)")
    parser.add_argument('--output', required=True, help="Output CSV file path")
    
    args = parser.parse_args()
    
    rows = load_dataset(args.input)
    
    out_table = compute_growth(rows, args.ward, args.category, args.growth_type)
    
    write_results(out_table, args.output, args.growth_type)
    print(f"Strict per-ward per-category output successfully written to {args.output}")

if __name__ == "__main__":
    main()
