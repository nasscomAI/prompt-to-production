import csv
import argparse
import os
import sys

def load_dataset(file_path):
    if not os.path.exists(file_path):
        return None, 0
    
    data = []
    null_count = 0
    with open(file_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row['actual_spend'] or row['actual_spend'].strip() == "":
                null_count += 1
            data.append(row)
    return data, null_count

def compute_growth(data, ward, category, growth_type):
    if not growth_type:
        print("Error: --growth-type must be specified. Valid options: MoM")
        sys.exit(1)
    
    if growth_type != "MoM":
        print(f"Error: Unsupported growth type '{growth_type}'. This agent only supports MoM currently.")
        sys.exit(1)

    # Filter data
    filtered = [row for row in data if row['ward'] == ward and row['category'] == category]
    
    # Sort by period
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    for i, row in enumerate(filtered):
        period = row['period']
        current_val_str = row['actual_spend'].strip()
        current_val = float(current_val_str) if current_val_str else None
        
        notes = row.get('notes', '')
        
        row_out = {
            'period': period,
            'ward': row['ward'],
            'category': row['category'],
            'actual_spend': current_val if current_val is not None else "NULL",
            'growth': "n/a",
            'formula': ""
        }
        
        if current_val is None:
            row_out['growth'] = f"NULL (Reason: {notes})"
            row_out['formula'] = "n/a"
        elif i > 0:
            prev_row = filtered[i-1]
            prev_val_str = prev_row['actual_spend'].strip()
            prev_val = float(prev_val_str) if prev_val_str else None
            
            if prev_val is None:
                row_out['growth'] = "NULL (Prev month null)"
                row_out['formula'] = f"({current_val} - NULL) / NULL"
            elif prev_val == 0:
                row_out['growth'] = "INF"
                row_out['formula'] = f"({current_val} - 0) / 0"
            else:
                growth = ((current_val - prev_val) / prev_val) * 100
                row_out['growth'] = f"{growth:+.1f}%"
                row_out['formula'] = f"(({current_val} - {prev_val}) / {prev_val}) * 100"
        else:
            row_out['growth'] = "Base Month"
            row_out['formula'] = "First period in set"
            
        results.append(row_out)
        
    return results

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    
    data, nulls = load_dataset(args.input)
    if data is None:
        print(f"Error: Input file {args.input} not found.")
        return
        
    print(f"Dataset loaded. Total rows: {len(data)}, Null actual_spend: {nulls}")

    # Aggregation check
    if args.ward.lower() == "any" or args.category.lower() == "any":
        print("Error: All-ward or all-category aggregation is strictly prohibited. Please specify a specific ward and category.")
        sys.exit(1)

    results = compute_growth(data, args.ward, args.category, args.growth_type)
    
    with open(args.output, mode='w', newline='', encoding='utf-8') as f:
        fieldnames = ['period', 'ward', 'category', 'actual_spend', 'growth', 'formula']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"Growth calculation complete. Results saved to {args.output}")

if __name__ == "__main__":
    main()
