"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
import sys

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]


def load_dataset(input_path: str) -> dict:
    """
    Reads CSV file, validates columns, reports null count and which rows have null actual_spend.
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            # Validate columns
            if not all(col in reader.fieldnames for col in REQUIRED_COLUMNS):
                missing = [col for col in REQUIRED_COLUMNS if col not in reader.fieldnames]
                raise ValueError(f"Missing required columns: {missing}")
            
            data = []
            null_rows = []
            
            for row in reader:
                # Handle null actual_spend
                actual_spend = row['actual_spend'].strip() if row['actual_spend'] else ''
                if actual_spend == '':
                    null_rows.append({
                        'period': row['period'],
                        'ward': row['ward'],
                        'category': row['category'],
                        'notes': row.get('notes', '')
                    })
                    row['actual_spend'] = None
                else:
                    try:
                        row['actual_spend'] = float(actual_spend)
                    except ValueError:
                        row['actual_spend'] = None
                
                row['budgeted_amount'] = float(row['budgeted_amount']) if row['budgeted_amount'] else 0
                data.append(row)
            
            return {
                'data': data,
                'columns': reader.fieldnames,
                'null_rows': null_rows
            }
    except FileNotFoundError:
        raise FileNotFoundError(f"Budget file not found: {input_path}")
    except Exception as e:
        raise Exception(f"Error reading budget file: {str(e)}")


def compute_growth(data: list, ward: str, category: str, growth_type: str) -> list:
    """
    Calculates MoM or YoY growth for a specific ward and category, handling nulls properly.
    """
    if not growth_type:
        raise ValueError("growth_type is required. Must be 'MoM' or 'YoY'.")
    
    if growth_type not in ['MoM', 'YoY']:
        raise ValueError("growth_type must be 'MoM' or 'YoY'")
    
    # Filter data for specific ward and category
    filtered = [row for row in data if row['ward'] == ward and row['category'] == category]
    
    if not filtered:
        raise ValueError(f"No data found for ward '{ward}' and category '{category}'")
    
    # Sort by period
    filtered.sort(key=lambda x: x['period'])
    
    # Build period index for lookups
    period_index = {row['period']: row for row in filtered}
    
    results = []
    
    for i, row in enumerate(filtered):
        period = row['period']
        actual_spend = row['actual_spend']
        notes = row.get('notes', '')
        
        result = {
            'period': period,
            'actual_spend': actual_spend,
            'growth_pct': None,
            'formula': None,
            'null_flag': None,
            'null_reason': None
        }
        
        # Handle null actual_spend
        if actual_spend is None:
            result['null_flag'] = 'NULL'
            result['null_reason'] = notes if notes else 'No data recorded'
            results.append(result)
            continue
        
        # Calculate growth
        if growth_type == 'MoM':
            # Previous month
            month = int(period.split('-')[1])
            year = int(period.split('-')[0])
            prev_month = month - 1
            prev_year = year
            if prev_month == 0:
                prev_month = 12
                prev_year = year - 1
            prev_period = f"{prev_year:04d}-{prev_month:02d}"
        else:  # YoY
            year = int(period.split('-')[0])
            prev_period = f"{year - 1}-{period.split('-')[1]}"
        
        # Get previous period data
        prev_row = period_index.get(prev_period)
        
        if prev_row and prev_row['actual_spend'] is not None:
            prev_spend = prev_row['actual_spend']
            if prev_spend != 0:
                growth = ((actual_spend - prev_spend) / prev_spend) * 100
                result['growth_pct'] = round(growth, 2)
                result['formula'] = f"(({actual_spend} - {prev_spend}) / {prev_spend}) * 100"
        
        results.append(result)
    
    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to budget CSV file")
    parser.add_argument("--ward", required=True, help="Ward name (e.g., 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=True, help="Category name (e.g., 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", required=True, choices=['MoM', 'YoY'], help="Growth type: MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write output CSV")
    args = parser.parse_args()
    
    # Load dataset
    dataset = load_dataset(args.input)
    print(f"Loaded {len(dataset['data'])} rows")
    print(f"Found {len(dataset['null_rows'])} null actual_spend values:")
    for nr in dataset['null_rows']:
        print(f"  - {nr['period']} | {nr['ward']} | {nr['category']}: {nr['notes']}")
    
    # Compute growth
    results = compute_growth(dataset['data'], args.ward, args.category, args.growth_type)
    
    # Write output
    try:
        with open(args.output, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['period', 'actual_spend', 'growth_pct', 'formula', 'null_flag', 'null_reason']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"Growth data written to {args.output}")
    except Exception as e:
        print(f"Error writing output file: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
