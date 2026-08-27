import argparse
import csv
import sys
import os

def load_dataset(file_path):
    """
    reads CSV, validates columns, reports null count and which rows before returning.
    """
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
        
    expected_columns = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
    
    dataset = []
    null_rows = []
    
    try:
        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Validate columns
            if not reader.fieldnames:
                print("Error: CSV file is empty.")
                sys.exit(1)
                
            missing_cols = [col for col in expected_columns if col not in reader.fieldnames]
            if missing_cols:
                print(f"Error: Missing expected columns: {', '.join(missing_cols)}")
                sys.exit(1)
                
            for row in reader:
                dataset.append(row)
                if not row['actual_spend'].strip():
                    null_rows.append(row)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
        
    if null_rows:
        print(f"Warning: Found {len(null_rows)} null values in 'actual_spend'.")
        for row in null_rows:
            print(f"  - Null row at {row['period']} for {row['ward']} - {row['category']}. Reason: {row['notes']}")
            
    return dataset, null_rows

def compute_growth(dataset, ward, category, growth_type):
    """
    takes ward + category + growth_type, returns per-period table with formula shown.
    """
    if not growth_type:
        print("Error: --growth-type is missing. Please specify a growth type (e.g., MoM, YoY). I will not guess.")
        sys.exit(1)
        
    # Enforcement: Never aggregate across wards or categories
    if not ward or not category:
        print("Error: Must specify both --ward and --category. Aggregating across wards or categories is not allowed.")
        sys.exit(1)
        
    # Filter and sort data
    filtered = [row for row in dataset if row['ward'] == ward and row['category'] == category]
    filtered.sort(key=lambda x: x['period'])
    
    if not filtered:
        print("No data found for the specified ward and category.")
        return []
        
    results = []
    
    if growth_type.lower() == 'mom':
        prev_spend = None
        for row in filtered:
            period = row['period']
            actual_str = row['actual_spend'].strip()
            
            if not actual_str:
                results.append({
                    'period': period,
                    'ward': ward,
                    'category': category,
                    'actual_spend': 'NULL',
                    'growth_type': growth_type,
                    'growth_value': 'NULL',
                    'formula': f"Null actual_spend - not computed. Reason: {row['notes']}"
                })
                prev_spend = None
                continue
                
            try:
                current_spend = float(actual_str)
            except ValueError:
                results.append({
                    'period': period,
                    'ward': ward,
                    'category': category,
                    'actual_spend': actual_str,
                    'growth_type': growth_type,
                    'growth_value': 'ERROR',
                    'formula': 'Invalid actual_spend value'
                })
                prev_spend = None
                continue
                
            if prev_spend is None:
                results.append({
                    'period': period,
                    'ward': ward,
                    'category': category,
                    'actual_spend': current_spend,
                    'growth_type': growth_type,
                    'growth_value': 'N/A',
                    'formula': 'N/A (first valid period or previous was null)'
                })
            else:
                growth_value = ((current_spend - prev_spend) / prev_spend) * 100
                sign = '+' if growth_value > 0 else ''
                formatted_growth = f"{sign}{growth_value:.1f}%"
                results.append({
                    'period': period,
                    'ward': ward,
                    'category': category,
                    'actual_spend': current_spend,
                    'growth_type': growth_type,
                    'growth_value': formatted_growth,
                    'formula': f"({current_spend} - {prev_spend}) / {prev_spend} * 100"
                })
                
            prev_spend = current_spend
    else:
        print(f"Error: Growth type '{growth_type}' is not supported yet.")
        sys.exit(1)
        
    return results

def main():
    parser = argparse.ArgumentParser(description='Budget Growth Calculator')
    parser.add_argument('--input', type=str, required=True, help='Input CSV file path')
    parser.add_argument('--ward', type=str, required=False, help='Target ward')
    parser.add_argument('--category', type=str, required=False, help='Target category')
    parser.add_argument('--growth-type', type=str, required=False, help='Type of growth (e.g., MoM)')
    parser.add_argument('--output', type=str, required=True, help='Output CSV file path')
    
    args = parser.parse_args()
    
    # Enforcement: Never aggregate across wards or categories unless explicitly instructed
    if not args.ward or not args.category:
        print("Error: Must specify both --ward and --category. Refusing to aggregate across boundaries.")
        sys.exit(1)
        
    # Enforcement: If --growth-type is not specified, refuse and ask
    if not args.growth_type:
        print("Error: --growth-type is missing. Please specify (e.g., MoM). Refusing to guess.")
        sys.exit(1)

    dataset, _ = load_dataset(args.input)
    
    results = compute_growth(dataset, args.ward, args.category, args.growth_type)
    
    if results:
        fieldnames = ['period', 'ward', 'category', 'actual_spend', 'growth_type', 'growth_value', 'formula']
        try:
            with open(args.output, mode='w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for row in results:
                    writer.writerow(row)
            print(f"Successfully wrote output to {args.output}")
        except Exception as e:
            print(f"Error writing to output file: {e}")
            sys.exit(1)

if __name__ == '__main__':
    main()
