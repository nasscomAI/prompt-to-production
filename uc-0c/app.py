"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
import sys
import os

def load_dataset(filepath):
    print(f"Loading dataset from: {filepath}")
    if not os.path.exists(filepath):
        print(f"Error: Dataset {filepath} not found.")
        sys.exit(1)
        
    expected_cols = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
    data = []
    null_rows = []
    
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        if not headers or [h.strip() for h in headers] != expected_cols:
            print(f"Error: Invalid columns in dataset. Expected: {expected_cols}, Got: {headers}")
            sys.exit(1)
            
        for row in reader:
            parsed_actual = float(row['actual_spend']) if row['actual_spend'].strip() else None
            parsed_budget = float(row['budgeted_amount']) if row['budgeted_amount'].strip() else 0.0
            
            row_dict = {
                'period': row['period'].strip(),
                'ward': row['ward'].strip(),
                'category': row['category'].strip(),
                'budgeted_amount': parsed_budget,
                'actual_spend': parsed_actual,
                'notes': row['notes'].strip()
            }
            data.append(row_dict)
            
            if parsed_actual is None:
                null_rows.append(row_dict)

    # Report nulls before returning
    print("--- Pre-Computation Validation Report ---")
    print(f"Found {len(null_rows)} explicitly null actual_spend values.")
    for nr in null_rows:
        print(f"  > NULL DETECTED at {nr['period']} | {nr['ward']} | {nr['category']} -> Note: {nr['notes']}")
    print("-----------------------------------------\n")
    
    return data

def compute_growth(data, target_ward, target_category, growth_type):
    # Enforce strict specific ward/category checks
    if target_ward.lower() in ['all', 'any', ''] or target_category.lower() in ['all', 'any', '']:
        print("Error: Aggregation across multiple wards or categories is directly forbidden. Please specify exactly one ward and one category.")
        sys.exit(1)
        
    filtered = [r for r in data if r['ward'].lower() == target_ward.lower() and r['category'].lower() == target_category.lower()]
    
    if not filtered:
        print(f"Warning: No data found for Ward: '{target_ward}' and Category: '{target_category}'")
    
    # Ensure they are sorted by period to accurately calculate period-over-period
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    
    if growth_type.upper() == 'MOM':
        for i in range(len(filtered)):
            current = filtered[i]
            prev = filtered[i-1] if i > 0 else None
            actual = current['actual_spend']
            
            # Condition: missing actual spend
            if actual is None:
                growth_str = f"NULL - {current['notes']}"
            else:
                if prev is None:
                    growth_str = "n/a (first period)"
                elif prev['actual_spend'] is None:
                    growth_str = "n/a (previous period was null)"
                elif prev['actual_spend'] == 0:
                    growth_str = "n/a (previous period was 0)"
                else:
                    prev_actual = prev['actual_spend']
                    pct = ((actual - prev_actual) / prev_actual) * 100
                    sign = "+" if pct > 0 else ""
                    growth_str = f"{sign}{pct:.1f}% (formula: (({actual} - {prev_actual}) / {prev_actual}) * 100)"
            
            results.append({
                'Ward': current['ward'],
                'Category': current['category'],
                'Period': current['period'],
                'Actual Spend (₹ lakh)': actual if actual is not None else "NULL",
                'Growth': growth_str
            })
    elif growth_type.upper() == 'YOY':
        for i in range(len(filtered)):
            current = filtered[i]
            year, month = current['period'].split('-')
            target_prev_period = f"{int(year)-1}-{month}"
            
            prev = next((r for r in filtered if r['period'] == target_prev_period), None)
            actual = current['actual_spend']
            
            if actual is None:
                growth_str = f"NULL - {current['notes']}"
            else:
                if prev is None:
                    growth_str = "n/a (no prior year data)"
                elif prev['actual_spend'] is None:
                    growth_str = "n/a (previous period was null)"
                elif prev['actual_spend'] == 0:
                    growth_str = "n/a (previous period was 0)"
                else:
                    prev_actual = prev['actual_spend']
                    pct = ((actual - prev_actual) / prev_actual) * 100
                    sign = "+" if pct > 0 else ""
                    growth_str = f"{sign}{pct:.1f}% (formula: (({actual} - {prev_actual}) / {prev_actual}) * 100)"
            
            results.append({
                'Ward': current['ward'],
                'Category': current['category'],
                'Period': current['period'],
                'Actual Spend (₹ lakh)': actual if actual is not None else "NULL",
                'Growth': growth_str
            })
    else:
        print(f"Error: Unsupported growth type '{growth_type}'. Only MoM and YoY are supported.")
        sys.exit(1)
        
    return results

def main():
    parser = argparse.ArgumentParser(description="Calculate precise budget growth metrics per Ward & Category.")
    parser.add_argument('--input', required=True, help="Path to input CSV dataset")
    parser.add_argument('--ward', required=True, help="Specific target ward name")
    parser.add_argument('--category', required=True, help="Specific target category name")
    parser.add_argument('--growth-type', required=False, help="Explicit computation type (e.g. MoM, YoY)")
    parser.add_argument('--output', required=True, help="Path to save output results CSV")
    
    args = parser.parse_args()
    
    # Enforce requirement 4: Refuse and ask if --growth-type is not specified, never guess.
    if not args.growth_type:
        print("Error: --growth-type not specified. Please explicitly define it (e.g. --growth-type MoM). The system refuses to guess.")
        sys.exit(1)
        
    # Process Load Dataset
    data = load_dataset(args.input)
    
    # Compute Growth
    results = compute_growth(data, args.ward, args.category, args.growth_type)
    
    # Save to output file
    try:
        with open(args.output, 'w', newline='', encoding='utf-8') as f:
            if not results:
                writer = csv.writer(f)
                writer.writerow(['Ward', 'Category', 'Period', 'Actual Spend (₹ lakh)', f'{args.growth_type} Growth'])
            else:
                out_headers = ['Ward', 'Category', 'Period', 'Actual Spend (₹ lakh)', f'{args.growth_type} Growth']
                writer = csv.writer(f)
                writer.writerow(out_headers)
                
                for row in results:
                    writer.writerow([row['Ward'], row['Category'], row['Period'], row['Actual Spend (₹ lakh)'], row['Growth']])
                    
        print(f"Success: Verified results safely written to {args.output}")
    except Exception as e:
        print(f"Error writing to {args.output}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
