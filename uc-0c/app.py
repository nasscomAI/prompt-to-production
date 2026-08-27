"""
UC-0C — Number That Looks Right
Budget Growth Calculator — per-ward per-category scoping, null awareness, formula transparency.
"""
import argparse
import csv
import sys
from collections import defaultdict
from datetime import datetime

# Known null rows from README
KNOWN_NULLS = {
    ("2024-03", "Ward 2 – Shivajinagar", "Drainage & Flooding"),
    ("2024-07", "Ward 4 – Warje", "Roads & Pothole Repair"),
    ("2024-11", "Ward 1 – Kasba", "Waste Management"),
    ("2024-08", "Ward 3 – Kothrud", "Parks & Greening"),
    ("2024-05", "Ward 5 – Hadapsar", "Streetlight Maintenance"),
}

def load_dataset(file_path):
    """Load budget CSV and report nulls."""
    data = defaultdict(dict)
    null_rows = []
    total_rows = 0
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row_num, row in enumerate(reader, start=2):
                total_rows += 1
                period = row.get('period', '').strip()
                ward = row.get('ward', '').strip()
                category = row.get('category', '').strip()
                budgeted = row.get('budgeted_amount', '').strip()
                actual = row.get('actual_spend', '').strip()
                notes = row.get('notes', '').strip()
                
                try:
                    budgeted_val = float(budgeted) if budgeted else None
                    actual_val = float(actual) if actual else None
                except ValueError:
                    print(f"WARNING: Row {row_num} has invalid number format", file=sys.stderr)
                    continue
                
                # Track nulls
                if not actual_val:
                    null_rows.append({
                        'period': period,
                        'ward': ward,
                        'category': category,
                        'notes': notes
                    })
                
                key = (period, ward, category)
                data[key] = {
                    'budgeted': budgeted_val,
                    'actual': actual_val,
                    'notes': notes
                }
    
    except FileNotFoundError:
        print(f"ERROR: File not found: {file_path}", file=sys.stderr)
        raise
    except Exception as e:
        print(f"ERROR: Failed to read CSV: {e}", file=sys.stderr)
        raise
    
    print(f"Loaded {total_rows} rows. Found {len(null_rows)} null actual_spend rows:", file=sys.stderr)
    for nr in null_rows:
        print(f"  - {nr['period']} | {nr['ward']} | {nr['category']} (reason: {nr['notes']})", file=sys.stderr)
    
    return dict(data), null_rows

def compute_growth(data, ward, category, growth_type='MoM'):
    """Compute growth metrics for (ward, category) pair."""
    
    # Validate inputs
    if growth_type not in ['MoM', 'YoY']:
        raise ValueError(f"growth_type must be 'MoM' or 'YoY', got '{growth_type}'")
    
    # Filter data for this (ward, category)
    filtered = []
    for (period, w, c), values in data.items():
        if w == ward and c == category:
            filtered.append((period, values))
    
    if not filtered:
        raise ValueError(f"No data found for ward='{ward}' and category='{category}'")
    
    # Sort by period
    filtered.sort(key=lambda x: x[0])
    
    # Check if ward/category exists
    if not filtered:
        raise ValueError(f"Ward '{ward}' or Category '{category}' not found in dataset")
    
    # Compute growth
    results = []
    prev_actual = None
    prev_period = None
    
    for i, (period, values) in enumerate(filtered):
        budgeted = values['budgeted']
        actual = values['actual']
        
        result = {
            'period': period,
            'budgeted_amount': budgeted,
            'actual_spend': actual,
            'growth_percent': None,
            'formula': '',
            'flag': ''
        }
        
        # Handle null actual_spend
        if actual is None:
            result['flag'] = 'NULL_MISSING'
            result['formula'] = f'(Null - cannot compute)'
            results.append(result)
            continue
        
        # Compute growth
        if growth_type == 'MoM':
            if i == 0:
                # First month - no prior data
                result['formula'] = 'First period - no prior month'
            elif prev_actual is not None:
                # Compute MoM
                growth_pct = ((actual - prev_actual) / prev_actual) * 100
                result['growth_percent'] = round(growth_pct, 1)
                result['formula'] = f'MoM = ({actual} - {prev_actual}) / {prev_actual} = {result["growth_percent"]}%'
            else:
                result['formula'] = f'Previous month is null - cannot compute'
        
        elif growth_type == 'YoY':
            # We don't have 2023 data, so refuse
            result['flag'] = 'INSUFFICIENT_DATA'
            result['formula'] = 'YoY requires 2023 data - not available'
        
        results.append(result)
        
        # Update for next iteration
        if actual is not None:
            prev_actual = actual
            prev_period = period
    
    return results

def write_output(results, output_path, ward, category, growth_type):
    """Write results to CSV."""
    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'period', 'ward', 'category', 'growth_type',
                'budgeted_amount', 'actual_spend', 'growth_percent', 
                'formula', 'flag'
            ])
            writer.writeheader()
            
            for result in results:
                writer.writerow({
                    'period': result['period'],
                    'ward': ward,
                    'category': category,
                    'growth_type': growth_type,
                    'budgeted_amount': result['budgeted_amount'],
                    'actual_spend': result['actual_spend'] if result['actual_spend'] is not None else '',
                    'growth_percent': result['growth_percent'] if result['growth_percent'] is not None else '',
                    'formula': result['formula'],
                    'flag': result['flag']
                })
    except IOError as e:
        print(f"ERROR: Failed to write output: {e}", file=sys.stderr)
        raise

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input",       required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward",        required=True, help="Ward name (e.g., 'Ward 1 – Kasba')")
    parser.add_argument("--category",    required=True, help="Category name (e.g., 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", default='MoM',  help="MoM or YoY (default: MoM)")
    parser.add_argument("--output",      required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()
    
    try:
        # Load data
        data, nulls = load_dataset(args.input)
        
        # Compute growth
        results = compute_growth(data, args.ward, args.category, args.growth_type)
        
        # Write output
        write_output(results, args.output, args.ward, args.category, args.growth_type)
        
        print(f"✓ Done. Growth computation written to {args.output}")
        
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

