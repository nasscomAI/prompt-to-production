"""
UC-0C app.py — Final Strict Implementation.
"""
import argparse
import csv
import sys

def is_previous_month(curr_str, prev_str):
    cy, cm = map(int, curr_str.split('-'))
    py, pm = map(int, prev_str.split('-'))
    if cm == 1:
        return py == cy - 1 and pm == 12
    else:
        return py == cy and pm == cm - 1

def validate_and_calculate(input_csv, output_csv, ward, category, growth_type):
    if not ward:
        sys.exit("ERROR: Refused calculation. Exactly one --ward must be specified to prevent cross-ward aggregation.")
    if not category:
        sys.exit("ERROR: Refused calculation. Exactly one --category must be specified to prevent cross-category aggregation.")
    if not growth_type or growth_type != "MoM":
        sys.exit("ERROR: Refused calculation. --growth-type must be specified as 'MoM'.")
        
    with open(input_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        data = list(reader)
        
    filtered = [r for r in data if r['ward'] == ward and r['category'] == category]
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    prev_spend = None
    prev_period = None
    
    for row in filtered:
        period_str = row['period']
        spend_str = row['actual_spend'].strip()
        notes = row['notes'].strip()
        
        result_row = {
            'period': period_str,
            'ward': ward,
            'category': category,
            'actual_spend': spend_str if spend_str else 'NULL',
            'previous_period': 'N/A',
            'previous_spend': 'N/A',
            'growth': 'N/A',
            'formula': 'N/A',
            'status': 'OK'
        }
        
        if not spend_str:
            result_row['status'] = f"NULL DATA: {notes}" if notes else "NULL DATA"
            results.append(result_row)
            prev_spend = None
            prev_period = period_str
            continue
            
        current_spend = float(spend_str)
        
        if prev_period is not None and prev_spend is not None:
            if is_previous_month(period_str, prev_period):
                result_row['previous_period'] = prev_period
                result_row['previous_spend'] = str(prev_spend)
                
                if prev_spend == 0:
                    result_row['status'] = "Cannot calculate (Division by Zero)"
                else:
                    growth = ((current_spend - prev_spend) / prev_spend) * 100
                    result_row['growth'] = f"{growth:+.1f}%"
                    result_row['formula'] = f"(({current_spend} - {prev_spend}) / {prev_spend}) * 100"
            else:
                result_row['status'] = "Missing previous month data"
        else:
            result_row['status'] = "No valid prior period"
            
        results.append(result_row)
        prev_spend = current_spend
        prev_period = period_str
        
    fieldnames = ['period', 'ward', 'category', 'actual_spend', 'previous_period', 'previous_spend', 'growth', 'formula', 'status']
    with open(output_csv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
        
    print(f"Summary written to {output_csv}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=False)
    parser.add_argument("--category", required=False)
    parser.add_argument("--growth-type", required=False)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    
    validate_and_calculate(args.input, args.output, args.ward, args.category, args.growth_type)
