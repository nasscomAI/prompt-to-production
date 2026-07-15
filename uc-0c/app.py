"""
UC-0C app.py — Number That Looks Right
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
import sys
from datetime import datetime

def load_dataset(file_path: str) -> list:
    """Reads the budget CSV file and reports any null values."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except Exception as e:
        raise ValueError(f"Could not read dataset: {e}")

    null_count = 0
    print("--- Null Value Report ---")
    for row in rows:
        val = row.get('actual_spend', '').strip()
        if not val or val.lower() == 'null':
            null_count += 1
            reason = row.get('notes', 'No reason provided')
            print(f"Null found: {row['period']} | {row['ward']} | {row['category']} -> {reason}")
    print(f"Total nulls found: {null_count}\n")
    
    return rows

def compute_growth(data: list, ward: str, category: str, growth_type: str, output_path: str):
    # Enforcement 1: Refuse aggregation
    if not ward or ward.lower() in ['any', 'all']:
        print("REFUSAL: Aggregation across multiple wards/categories is not permitted by default. Please specify a single ward and category.")
        sys.exit(1)
    if not category or category.lower() in ['any', 'all']:
        print("REFUSAL: Aggregation across multiple wards/categories is not permitted by default. Please specify a single ward and category.")
        sys.exit(1)
        
    # Enforcement 4: Refuse if growth_type not specified
    if not growth_type:
        print("REFUSAL: Please specify --growth-type (e.g. MoM or YoY). I cannot guess the required metric.")
        sys.exit(1)
        
    growth_type = growth_type.upper()
    if growth_type not in ['MOM', 'YOY']:
        print(f"REFUSAL: Unsupported growth type '{growth_type}'. Use MoM or YoY.")
        sys.exit(1)
        
    # Filter data
    filtered_data = [r for r in data if r['ward'] == ward and r['category'] == category]
    
    if not filtered_data:
        print(f"Warning: No data found for Ward: '{ward}', Category: '{category}'")
    
    # Sort by period
    filtered_data.sort(key=lambda x: x['period'])
    
    # Create lookup for easy previous value retrieval
    spend_lookup = {}
    for r in filtered_data:
        val = r.get('actual_spend', '').strip()
        if val and val.lower() != 'null':
            spend_lookup[r['period']] = float(val)
        else:
            spend_lookup[r['period']] = None
            
    output_rows = []
    
    for r in filtered_data:
        period = r['period'] # format YYYY-MM
        year = int(period.split('-')[0])
        month = int(period.split('-')[1])
        
        if growth_type == 'MOM':
            prev_month = month - 1
            prev_year = year
            if prev_month == 0:
                prev_month = 12
                prev_year -= 1
        else: # YOY
            prev_month = month
            prev_year = year - 1
            
        prev_period = f"{prev_year}-{prev_month:02d}"
        
        current_val = spend_lookup.get(period)
        prev_val = spend_lookup.get(prev_period, 'MISSING')
        
        formula = f"((actual_{period} - actual_{prev_period}) / actual_{prev_period}) * 100"
        
        notes = r.get('notes', '')
        
        if current_val is None:
            growth_value = 'NULL'
            notes = f"Cannot compute: Current period actual_spend is null. Reason: {notes}".strip()
        elif prev_val == 'MISSING':
            growth_value = 'n/a'
            notes = "Cannot compute: Previous period data unavailable in dataset."
        elif prev_val is None:
            growth_value = 'NULL'
            notes = "Cannot compute: Previous period actual_spend is null."
        elif prev_val == 0:
            growth_value = 'n/a'
            notes = "Cannot compute: Previous period actual_spend is zero (division by zero)."
        else:
            growth_calc = ((current_val - prev_val) / prev_val) * 100
            growth_value = f"{growth_calc:+.1f}%"
            
        output_rows.append({
            'period': period,
            'ward': ward,
            'category': category,
            'actual_spend': current_val if current_val is not None else 'NULL',
            'growth_type': growth_type,
            'growth_value': growth_value,
            'formula': formula,
            'notes': notes
        })
        
    fieldnames = ['period', 'ward', 'category', 'actual_spend', 'growth_type', 'growth_value', 'formula', 'notes']
    
    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(output_rows)
        print(f"Successfully wrote {len(output_rows)} rows to {output_path}")
    except IOError as e:
        raise IOError(f"Could not write to {output_path}: {e}")


def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to input budget CSV")
    parser.add_argument("--ward", help="Target ward name")
    parser.add_argument("--category", help="Target category name")
    parser.add_argument("--growth-type", help="MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    
    args = parser.parse_args()
    
    try:
        data = load_dataset(args.input)
        compute_growth(
            data=data,
            ward=args.ward,
            category=args.category,
            growth_type=args.growth_type,
            output_path=args.output
        )
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
