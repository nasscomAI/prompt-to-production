"""
UC-0C app.py
Heuristic, rule-based implementation of growth computation.
"""
import argparse
import csv
import sys
import os

def load_dataset(input_path: str):
    if not os.path.exists(input_path):
        print(f"Error: File {input_path} not found.")
        sys.exit(1)
        
    data = []
    null_count = 0
    null_rows = []
    
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            # Validate actual_spend
            spend = row.get('actual_spend', '').strip()
            if not spend or spend.lower() in ['null', 'none']:
                null_count += 1
                null_rows.append(f"Row {i+2}: {row.get('period')} - {row.get('ward')} - {row.get('category')} (Note: {row.get('notes')})")
            data.append(row)
            
    print(f"Dataset loaded. Found {null_count} null 'actual_spend' values.")
    if null_count > 0:
        for nr in null_rows:
            print(f" - {nr}")
            
    return data

def compute_growth(data, ward, category, growth_type):
    if not ward or not category or ward.lower() == 'all' or category.lower() == 'all':
        print("Error: Aggregation across wards or categories is strictly prohibited. You must specify a single ward and category.")
        sys.exit(1)
        
    if not growth_type:
        print("Error: --growth-type must be specified (e.g., MoM). Refusing to guess the calculation method.")
        sys.exit(1)
        
    # Filter data
    filtered = [d for d in data if d.get('ward') == ward and d.get('category') == category]
    
    # Sort by period
    filtered.sort(key=lambda x: x.get('period'))
    
    results = []
    prev_spend = None
    
    for row in filtered:
        period = row.get('period')
        spend_str = row.get('actual_spend', '').strip()
        
        result_row = {
            'Ward': ward,
            'Category': category,
            'Period': period,
            'Actual Spend': spend_str if spend_str else 'NULL',
            'Computed Growth': '',
            'Formula Used': ''
        }
        
        if not spend_str or spend_str.lower() in ['null', 'none']:
            result_row['Computed Growth'] = f"FLAGGED: {row.get('notes')}"
            result_row['Formula Used'] = "N/A - Missing Data"
            prev_spend = None  # Reset previous spend
        else:
            try:
                current_spend = float(spend_str)
            except ValueError:
                result_row['Computed Growth'] = "ERROR: Invalid Spend"
                result_row['Formula Used'] = "N/A"
                prev_spend = None
                results.append(result_row)
                continue
                
            if prev_spend is None:
                result_row['Computed Growth'] = "N/A"
                result_row['Formula Used'] = "N/A - No previous period data"
            else:
                if growth_type.lower() == 'mom':
                    if prev_spend == 0:
                        result_row['Computed Growth'] = "Infinity"
                        result_row['Formula Used'] = f"({current_spend} - 0) / 0"
                    else:
                        growth = ((current_spend - prev_spend) / prev_spend) * 100
                        sign = "+" if growth > 0 else ""
                        result_row['Computed Growth'] = f"{sign}{growth:.1f}%"
                        result_row['Formula Used'] = f"({current_spend} - {prev_spend}) / {prev_spend} * 100"
                else:
                    result_row['Computed Growth'] = "ERROR: Unknown Growth Type"
                    result_row['Formula Used'] = "N/A"
            
            prev_spend = current_spend
            
        results.append(result_row)
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    parser.add_argument("--ward", required=False, help="Specific ward to filter")
    parser.add_argument("--category", required=False, help="Specific category to filter")
    parser.add_argument("--growth-type", dest="growth_type", required=False, help="Type of growth to compute (e.g., MoM)")
    
    args = parser.parse_args()
    
    data = load_dataset(args.input)
    
    results = compute_growth(data, args.ward, args.category, args.growth_type)
    
    if not results:
        print("Warning: No matching rows found for the specified ward and category.")
    
    # Write output
    fieldnames = ['Ward', 'Category', 'Period', 'Actual Spend', 'Computed Growth', 'Formula Used']
    with open(args.output, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
        
    print(f"Processed {len(results)} rows. Results written to {args.output}")

if __name__ == "__main__":
    main()
