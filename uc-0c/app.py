import argparse
import csv
import sys
import os

def load_dataset(input_path):
    """Skill: load_dataset"""
    if not os.path.exists(input_path):
        print(f"Error: File {input_path} not found.")
        sys.exit(1)
    
    data = []
    null_rows = []
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            # Validate columns
            expected = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
            if not all(col in (reader.fieldnames or []) for col in expected):
                print(f"Error: Invalid CSV format. Expected: {expected}")
                sys.exit(1)
            
            for row in reader:
                if not row['actual_spend'] or row['actual_spend'].strip() == '':
                    null_rows.append(row)
                data.append(row)
                
    except Exception as e:
        print(f"Error loading CSV: {e}")
        sys.exit(1)
        
    print(f"Dataset Loaded. Total Rows: {len(data)}. Found {len(null_rows)} null entries in 'actual_spend'.")
    return data

def compute_growth(data, ward, category, growth_type):
    """Skill: compute_growth"""
    # Refusal logic if growth_type is missing
    if not growth_type:
        print("Enforcement Error: --growth-type is mandatory. Do not guess MoM or YoY.")
        sys.exit(1)
    
    # Identify unique wards and categories to process
    if ward:
        wards = [ward]
    else:
        wards = sorted(list(set(r['ward'] for r in data)))
        
    if category:
        categories = [category]
    else:
        categories = sorted(list(set(r['category'] for r in data)))
    
    all_results = []
    
    for current_ward in wards:
        for current_category in categories:
            # Filter for specific ward and category (STRICT GRANULARITY)
            filtered = [r for r in data if r['ward'] == current_ward and r['category'] == current_category]
            
            if not filtered:
                continue

            # Sort by period
            filtered.sort(key=lambda x: x['period'])
            
            for i, current in enumerate(filtered):
                row_result = {
                    'period': current['period'],
                    'ward': current['ward'],
                    'category': current['category'],
                    'actual_spend': current['actual_spend'] if current['actual_spend'] else 'NULL',
                    'growth_percentage': 'N/A',
                    'formula': 'N/A',
                    'notes': current['notes']
                }
                
                # Check if current value is null
                if not current['actual_spend'] or current['actual_spend'].strip() == '':
                    row_result['growth_percentage'] = 'FLAGGED'
                    row_result['formula'] = f"NULL Value Found: {current['notes']}"
                    all_results.append(row_result)
                    continue
                    
                current_val = float(current['actual_spend'])
                prev_row = None
                
                if growth_type == 'MoM':
                    if i > 0:
                        prev_row = filtered[i-1]
                elif growth_type == 'YoY':
                    curr_period = current['period']
                    try:
                        curr_year = int(curr_period[:4])
                        curr_month = curr_period[5:]
                        prev_year_period = f"{curr_year-1}-{curr_month}"
                        p_rows = [r for r in filtered if r['period'] == prev_year_period]
                        if p_rows:
                            prev_row = p_rows[0]
                    except:
                        pass
                
                if prev_row:
                    if not prev_row['actual_spend'] or prev_row['actual_spend'].strip() == '':
                        row_result['growth_percentage'] = 'N/A'
                        row_result['formula'] = f"Prev NULL: {prev_row['notes']}"
                    else:
                        prev_val = float(prev_row['actual_spend'])
                        if prev_val != 0:
                            growth = ((current_val - prev_val) / prev_val) * 100
                            row_result['growth_percentage'] = f"{growth:+.1f}%"
                            row_result['formula'] = f"({current_val} - {prev_val}) / {prev_val}"
                        else:
                            row_result['growth_percentage'] = 'N/A'
                            row_result['formula'] = "Div by zero"
                else:
                    row_result['growth_percentage'] = 'N/A'
                    row_result['formula'] = "No comparison period"
                    
                all_results.append(row_result)
        
    return all_results

def main():
    parser = argparse.ArgumentParser(description="Calculate budget growth for PMC data.")
    parser.add_argument("--input", required=True, help="Path to input budget CSV")
    parser.add_argument("--ward", help="Specific ward name (optional for all)")
    parser.add_argument("--category", help="Specific category name (optional for all)")
    parser.add_argument("--growth-type", choices=['MoM', 'YoY'], help="Type of growth calculation")
    parser.add_argument("--output", required=True, help="Path to save output CSV")
    
    args = parser.parse_args()
    
    # 1. Load Data
    dataset = load_dataset(args.input)
    
    # 2. Refusal condition check for growth-type
    if not args.growth_type:
        print("Enforcement Error: --growth-type is mandatory.")
        sys.exit(1)
        
    # 3. Aggregation check: Ensure user didn't request total summing
    if args.ward and args.ward.lower() in ['all', 'total', 'any'] or \
       args.category and args.category.lower() in ['all', 'total', 'any']:
        print("Enforcement Error: Aggregate 'all-ward' summing is prohibited.")
        sys.exit(1)
        
    # 4. Compute Growth
    results = compute_growth(dataset, args.ward, args.category, args.growth_type)
    
    # 5. Save output
    if results:
        fieldnames = ['period', 'ward', 'category', 'actual_spend', 'growth_percentage', 'formula', 'notes']
        try:
            with open(args.output, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
            print(f"Success: Full growth details saved to {args.output}")
        except Exception as e:
            print(f"Error saving output: {e}")

if __name__ == "__main__":
    main()
