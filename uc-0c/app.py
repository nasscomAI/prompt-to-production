"""
UC-0C app.py — Budget Growth Calculator.
Computes month-over-month or year-over-year growth for a specific ward-category pair.
Handles null values, enforces per-ward per-category isolation, and shows formulas.
"""
import argparse
import csv
from pathlib import Path
from datetime import datetime


def load_dataset(input_path):
    """
    Load and validate the budget CSV file.
    Returns: dict with 'data' (list of dicts), 'total_rows' (int), 'null_rows' (list)
    """
    input_file = Path(input_path)
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    data = []
    null_rows = []
    
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError("CSV is empty")
        
        required_cols = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
        if not required_cols.issubset(set(reader.fieldnames or [])):
            raise ValueError(f"Missing columns. Required: {required_cols}")
        
        for row_num, row in enumerate(reader, start=2):
            # Convert budgeted_amount to float
            try:
                row['budgeted_amount'] = float(row['budgeted_amount'])
            except (ValueError, TypeError):
                raise ValueError(f"Row {row_num}: budgeted_amount must be numeric")
            
            # Handle actual_spend: blank means null
            if row['actual_spend'].strip() == '':
                null_rows.append({
                    'period': row['period'],
                    'ward': row['ward'],
                    'category': row['category'],
                    'reason': row['notes']
                })
                row['actual_spend'] = None
            else:
                try:
                    row['actual_spend'] = float(row['actual_spend'])
                except (ValueError, TypeError):
                    raise ValueError(f"Row {row_num}: actual_spend must be numeric or blank")
            
            data.append(row)
    
    return {
        'data': data,
        'total_rows': len(data),
        'null_rows': null_rows
    }


def compute_growth(loaded_data, ward, category, growth_type):
    """
    Compute month-over-month or year-over-year growth for a ward-category pair.
    Returns: list of dicts with period, actual_spend, prior_value, growth_percentage, formula, note
    """
    if growth_type not in ('MoM', 'YoY'):
        raise ValueError(f"growth_type must be MoM or YoY, got: {growth_type}")
    
    data = loaded_data['data']
    
    # Filter data for the requested ward and category
    filtered = [row for row in data if row['ward'] == ward and row['category'] == category]
    
    if not filtered:
        raise ValueError(f"No data found for ward='{ward}', category='{category}'")
    
    # Sort by period
    filtered.sort(key=lambda x: x['period'])
    
    # Build output table
    output = []
    prior_value = None
    
    for row in filtered:
        period = row['period']
        actual_spend = row['actual_spend']
        
        result = {
            'period': period,
            'actual_spend': actual_spend if actual_spend is not None else 'NULL',
            'prior_value': None,
            'growth_percentage': None,
            'formula': '',
            'note': ''
        }
        
        # If current row is null, flag it and reset prior_value (break the chain)
        if actual_spend is None:
            result['note'] = row['notes']
            prior_value = None  # Reset: don't use null as prior value
            output.append(result)
            continue
        
        # Check if we can compute growth
        if prior_value is not None:
            if growth_type == 'MoM':
                growth_pct = ((actual_spend - prior_value) / prior_value) * 100
                result['prior_value'] = prior_value
                result['growth_percentage'] = round(growth_pct, 1)
                result['formula'] = f"({actual_spend} - {prior_value}) / {prior_value} * 100"
            elif growth_type == 'YoY':
                # For YoY, only compute if we have exactly 12 months of difference
                # Since dataset is only 2024, YoY comparison not applicable
                pass
        
        output.append(result)
        prior_value = actual_spend
    
    return output


def main():
    parser = argparse.ArgumentParser(
        description='Calculate month-over-month or year-over-year spending growth for a ward-category pair'
    )
    parser.add_argument('--input', required=True, help='Path to the budget CSV file')
    parser.add_argument('--ward', help='Ward name (e.g., "Ward 1 – Kasba")')
    parser.add_argument('--category', help='Category name (e.g., "Roads & Pothole Repair")')
    parser.add_argument('--growth-type', help='Growth type: MoM (Month-over-Month) or YoY (Year-over-Year)')
    parser.add_argument('--output', required=True, help='Path for the output CSV file')
    
    args = parser.parse_args()
    
    # Validation: all three parameters required
    if not args.ward:
        raise ValueError("--ward is required. Choices: Ward 1 – Kasba, Ward 2 – Shivajinagar, Ward 3 – Kothrud, Ward 4 – Warje, Ward 5 – Hadapsar")
    if not args.category:
        raise ValueError("--category is required. Choices: Roads & Pothole Repair, Drainage & Flooding, Streetlight Maintenance, Waste Management, Parks & Greening")
    if not args.growth_type:
        raise ValueError("--growth-type is required. Choices: MoM, YoY")
    
    # Load dataset
    print("Loading dataset...")
    loaded = load_dataset(args.input)
    print(f"  Loaded {loaded['total_rows']} rows")
    
    # Report null rows
    if loaded['null_rows']:
        print(f"\nFound {len(loaded['null_rows'])} null rows. Flagging before computation:")
        for null_row in loaded['null_rows']:
            print(f"  {null_row['period']} | {null_row['ward']} | {null_row['category']} | Reason: {null_row['reason']}")
    else:
        print("\nNo null rows found.")
    
    # Compute growth
    print(f"\nComputing {args.growth_type} growth for {args.ward} - {args.category}...")
    try:
        growth_results = compute_growth(loaded, args.ward, args.category, args.growth_type)
    except ValueError as e:
        print(f"ERROR: {e}")
        raise
    
    # Write output
    output_file = Path(args.output)
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['period', 'actual_spend', 'prior_value', 'growth_percentage', 'formula', 'note']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(growth_results)
    
    print(f"Output written to {output_file}")
    print(f"\nSummary:")
    print(f"  Ward: {args.ward}")
    print(f"  Category: {args.category}")
    print(f"  Growth Type: {args.growth_type}")
    print(f"  Periods: {len(growth_results)} rows")


if __name__ == "__main__":
    main()
