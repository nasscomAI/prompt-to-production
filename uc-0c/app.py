"""
UC-0C app.py — Enforced Number That Looks Right.
Implements the rules from agents.md and skills.md.
"""
import argparse
import csv
import sys
import os

REQUIRED_COLUMNS = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']

def load_dataset(filepath):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        if not headers:
            raise ValueError("CSV file is empty or missing headers")
            
        for col in REQUIRED_COLUMNS:
            if col not in headers:
                raise ValueError(f"Missing required column: {col}")
        
        data = []
        null_count: int = 0
        for i, row in enumerate(reader, start=1):
            actual_spend = row.get('actual_spend', '').strip()
            # Rule 2 in action: Check for null/empty actual_spend
            if not actual_spend:
                null_count += 1
                reason = row.get('notes', 'No reason provided')
                print(f"FLAG: Null actual_spend found before compute - Period '{row.get('period')}', Ward '{row.get('ward')}', Category '{row.get('category')}'. Reason: {reason}")
            data.append(row)
            
    print(f"Dataset loaded. Total rows: {len(data)}. Rows with null actual_spend globally: {null_count}")
    return data

def compute_growth(data, ward, category, growth_type):
    # Rule 1: Never aggregate across wards or categories unless explicitly instructed — refuse if asked
    if not ward or ward.lower() in ("any", "all"):
        raise ValueError("REFUSAL: Cannot aggregate across wards. You must specify a single, specific ward.")
    if not category or category.lower() in ("any", "all"):
        raise ValueError("REFUSAL: Cannot aggregate across categories. You must specify a single, specific category.")
    
    # Strictly filter dataset for the specific ward and category
    filtered = [row for row in data if row['ward'] == ward and row['category'] == category]
    
    if not filtered:
        print(f"Warning: No data found for ward '{ward}' and category '{category}'.")
        return []
        
    # Sort chronologically by period (YYYY-MM)
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    
    for i in range(len(filtered)):
        current_row = filtered[i]
        period = current_row['period']
        budget = current_row['budgeted_amount']
        spend_str = current_row['actual_spend'].strip()
        
        result_row = {
            'period': period,
            'ward': ward,
            'category': category,
            'budgeted_amount': budget,
            'actual_spend': spend_str,
            'growth_percentage': '',
            'formula': ''
        }
        
        # Rule 2 continuation: Explicitly flag null rows in output instead of ignoring
        if not spend_str:
            result_row['growth_percentage'] = f"FLAGGED: {current_row.get('notes')}"
            result_row['formula'] = "n/a (spend is null)"
            results.append(result_row)
            continue
            
        current_spend = float(spend_str)
        
        if growth_type.upper() == 'MOM':
            if i == 0:
                result_row['growth_percentage'] = "n/a"
                result_row['formula'] = "n/a (first period)"
                results.append(result_row)
                continue
                
            prev_spend_str = filtered[i-1]['actual_spend'].strip()
            if not prev_spend_str:
                result_row['growth_percentage'] = "n/a"
                result_row['formula'] = f"n/a (previous period {filtered[i-1]['period']} is null)"
                results.append(result_row)
                continue
                
            prev_spend = float(prev_spend_str)
            if prev_spend == 0:
                result_row['growth_percentage'] = "n/a"
                result_row['formula'] = "n/a (previous period is zero)"
                results.append(result_row)
                continue
                
            growth = (current_spend - prev_spend) / prev_spend * 100
            # Rule 3: Show formula used in every output row alongside the result
            result_row['growth_percentage'] = f"{growth:+.1f}%"
            result_row['formula'] = f"({current_spend} - {prev_spend}) / {prev_spend} * 100"
            results.append(result_row)
            
        elif growth_type.upper() == 'YOY':
            if i < 12:
                result_row['growth_percentage'] = "n/a"
                result_row['formula'] = "n/a (no prior year data)"
                results.append(result_row)
                continue
                
            prev_spend_str = filtered[i-12]['actual_spend'].strip()
            if not prev_spend_str:
                result_row['growth_percentage'] = "n/a"
                result_row['formula'] = f"n/a (previous year period {filtered[i-12]['period']} is null)"
                results.append(result_row)
                continue
                
            prev_spend = float(prev_spend_str)
            if prev_spend == 0:
                result_row['growth_percentage'] = "n/a"
                result_row['formula'] = "n/a (previous period is zero)"
                results.append(result_row)
                continue
                
            growth = (current_spend - prev_spend) / prev_spend * 100
            result_row['growth_percentage'] = f"{growth:+.1f}%"
            result_row['formula'] = f"({current_spend} - {prev_spend}) / {prev_spend} * 100"
            results.append(result_row)
        else:
            result_row['growth_percentage'] = f"Unsupported growth type: {growth_type}"
            result_row['formula'] = "n/a"
            results.append(result_row)
            
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Number That Looks Right")
    parser.add_argument("--input", required=True, help="Input CSV filepath")
    parser.add_argument("--ward", required=True, help="Ward name")
    parser.add_argument("--category", required=True, help="Category name")
    parser.add_argument("--growth-type", required=False, help="Type of growth to compute (e.g. MoM, YoY)")
    parser.add_argument("--output", required=True, help="Output CSV filepath")

    args = parser.parse_args()

    # Rule 4: If --growth-type not specified — refuse and ask, never guess
    if not args.growth_type:
        print("REFUSAL: --growth-type not specified. Please specify a growth type (e.g. MoM) rather than assuming one.")
        sys.exit(1)

    try:
        dataset = load_dataset(args.input)
        computed = compute_growth(dataset, args.ward, args.category, args.growth_type)
        
        # Write output
        if computed:
            fieldnames = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'growth_percentage', 'formula']
            with open(args.output, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for row in computed:
                    writer.writerow(row)
            print(f"Success. Wrote output to {args.output}")
        else:
            print("No data was computed.")
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
