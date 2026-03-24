import argparse
import csv
import sys
import os

def load_dataset(file_path):
    """skills: load_dataset — reads CSV, validates columns, reports null count and which rows before returning"""
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        sys.exit(1)
        
    data = []
    null_rows = []
    required_columns = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
    
    with open(file_path, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        if not all(col in reader.fieldnames for col in required_columns):
            print(f"Error: Missing required columns. Found: {reader.fieldnames}")
            sys.exit(1)
            
        for i, row in enumerate(reader, start=2):
            if not row['actual_spend'] or row['actual_spend'].strip() == '':
                null_rows.append((i, row))
            data.append(row)
            
    if null_rows:
        print(f"Found {len(null_rows)} null actual_spend values:")
        for line_num, row in null_rows:
            print(f"  Line {line_num}: {row['period']} | {row['ward']} | {row['category']} - Reason: {row['notes']}")
            
    return data

def compute_growth(data, ward, category, growth_type):
    """skills: compute_growth — takes ward + category + growth_type, returns per-period table with formula shown"""
    # Filter data
    filtered = [r for r in data if r['ward'] == ward and r['category'] == category]
    
    if not filtered:
        print(f"No data found for Ward: {ward}, Category: {category}")
        return []
        
    # Sort by period
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    for i in range(len(filtered)):
        curr = filtered[i]
        curr_val_str = curr['actual_spend'].strip()
        
        res_row = {
            'ward': curr['ward'],
            'category': curr['category'],
            'period': curr['period'],
            'actual_spend': curr_val_str if curr_val_str else 'NULL',
            'growth': 'n/a',
            'formula': 'n/a'
        }
        
        if not curr_val_str:
            res_row['growth'] = 'FLAGGED'
            res_row['formula'] = f"Null detected: {curr['notes']}"
            results.append(res_row)
            continue

        if i == 0:
            res_row['growth'] = 'n/a (first period)'
            res_row['formula'] = 'n/a'
        else:
            prev = filtered[i-1]
            prev_val_str = prev['actual_spend'].strip()
            
            if not prev_val_str:
                res_row['growth'] = 'n/a (prev null)'
                res_row['formula'] = f"Cannot compute: Prev value null ({prev['notes']})"
            else:
                curr_val = float(curr_val_str)
                prev_val = float(prev_val_str)
                
                if growth_type == 'MoM':
                    if prev_val == 0:
                        growth_pct = 0.0 # Handle division by zero if necessary
                        formula = f"({curr_val} - {prev_val}) / {prev_val}"
                    else:
                        growth_pct = ((curr_val - prev_val) / prev_val) * 100
                        formula = f"({curr_val} - {prev_val}) / {prev_val}"
                    
                    res_row['growth'] = f"{'+' if growth_pct > 0 else ''}{growth_pct:.1f}%"
                    res_row['formula'] = formula
                else:
                    # YoY implementation would look back 12 months, but dataset is only 12 months 2024
                    res_row['growth'] = 'YoY not supported for single year dataset'
                    res_row['formula'] = 'n/a'
                    
        results.append(res_row)
        
    return results

def main():
    parser = argparse.ArgumentParser(description="Budget Growth Analysis Script")
    parser.add_argument("--input", required=True, help="Input CSV file path")
    parser.add_argument("--ward", required=True, help="Ward name")
    parser.add_argument("--category", required=True, help="Category name")
    parser.add_argument("--growth-type", help="Growth type (MoM or YoY)")
    parser.add_argument("--output", required=True, help="Output CSV file path")
    
    args = parser.parse_args()
    
    # Enforcement 4: If --growth-type not specified — refuse and ask, never guess
    if not args.growth_type:
        print("Refusal: --growth-type not specified. Please specify MoM or YoY.")
        sys.exit(1)
        
    # Enforcement 1: Never aggregate across wards or categories
    # This is implicitly handled by requiring --ward and --category and filtering by them exactly.
    
    data = load_dataset(args.input)
    results = compute_growth(data, args.ward, args.category, args.growth_type)
    
    if results:
        with open(args.output, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['ward', 'category', 'period', 'actual_spend', 'growth', 'formula'])
            writer.writeheader()
            writer.writerows(results)
        print(f"Output saved to {args.output}")

if __name__ == "__main__":
    main()
