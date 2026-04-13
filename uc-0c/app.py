#!/usr/bin/env python3
"""
UC-0C: Number That Looks Right
Calculates budget growth with proper aggregation scope and null handling.
"""

import csv
import argparse
import sys
from pathlib import Path
from datetime import datetime


def load_dataset(file_path):
    """
    Load budget dataset and report null values.
    
    Args:
        file_path: Path to ward_budget.csv
    
    Returns:
        dict with data (list of dicts), null_report, null_count
    """
    if not Path(file_path).exists():
        print(f"Error: Dataset file '{file_path}' not found", file=sys.stderr)
        sys.exit(1)
    
    data = []
    null_report = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Check for null actual_spend
            if not row['actual_spend'] or row['actual_spend'].strip() == '':
                null_report.append({
                    'period': row['period'],
                    'ward': row['ward'],
                    'category': row['category'],
                    'reason': row['notes']
                })
                row['actual_spend'] = None
            else:
                row['actual_spend'] = float(row['actual_spend'])
            
            # Convert budgeted_amount
            if row['budgeted_amount']:
                row['budgeted_amount'] = float(row['budgeted_amount'])
            
            data.append(row)
    
    # Print null report
    print(f"\nFound {len(null_report)} null actual_spend values:")
    for null_row in null_report:
        print(f"  - {null_row['period']}, {null_row['ward']}, {null_row['category']}: {null_row['reason']}")
    print()
    
    return {
        'data': data,
        'null_report': null_report,
        'null_count': len(null_report)
    }


def compute_growth(dataset, ward, category, growth_type, output_file):
    """
    Compute growth for specific ward and category.
    
    Args:
        dataset: Output from load_dataset
        ward: Ward name
        category: Category name
        growth_type: "MoM" or "YoY"
        output_file: Output CSV path
    """
    # Validate growth_type
    if not growth_type:
        print("Error: --growth-type must be specified (MoM or YoY)", file=sys.stderr)
        sys.exit(1)
    
    if growth_type not in ['MoM', 'YoY']:
        print(f"Error: Invalid growth_type '{growth_type}'. Must be 'MoM' or 'YoY'", file=sys.stderr)
        sys.exit(1)
    
    # Filter data to ward and category
    filtered_data = [
        row for row in dataset['data']
        if row['ward'] == ward and row['category'] == category
    ]
    
    if not filtered_data:
        print(f"Error: No data found for ward='{ward}', category='{category}'", file=sys.stderr)
        sys.exit(1)
    
    # Sort by period
    filtered_data.sort(key=lambda x: x['period'])
    
    print(f"Computing {growth_type} growth for {ward}, {category}")
    print(f"Found {len(filtered_data)} periods\n")
    
    # Compute growth for each period
    results = []
    
    for i, row in enumerate(filtered_data):
        period = row['period']
        actual_spend = row['actual_spend']
        
        result = {
            'period': period,
            'ward': ward,
            'category': category,
            'actual_spend': actual_spend if actual_spend is not None else '',
            'growth_pct': '',
            'formula': '',
            'flag': ''
        }
        
        # Check if current value is null
        if actual_spend is None:
            # Find reason from null_report
            reason = ''
            for null_row in dataset['null_report']:
                if (null_row['period'] == period and 
                    null_row['ward'] == ward and 
                    null_row['category'] == category):
                    reason = null_row['reason']
                    break
            
            result['growth_pct'] = 'N/A'
            result['formula'] = 'Cannot compute - null value'
            result['flag'] = f'NULL_VALUE: {reason}'
            results.append(result)
            continue
        
        # Compute growth based on type
        if growth_type == 'MoM':
            # Month-over-Month
            if i == 0:
                result['growth_pct'] = 'N/A'
                result['formula'] = 'First period - no previous month'
                result['flag'] = 'No previous period'
            else:
                prev_row = filtered_data[i - 1]
                prev_spend = prev_row['actual_spend']
                
                if prev_spend is None:
                    result['growth_pct'] = 'N/A'
                    result['formula'] = 'Cannot compute - previous period null'
                    result['flag'] = 'Previous period null'
                else:
                    growth = ((actual_spend - prev_spend) / prev_spend) * 100
                    result['growth_pct'] = f"{growth:+.1f}%"
                    result['formula'] = f"({actual_spend} - {prev_spend}) / {prev_spend} * 100"
        
        elif growth_type == 'YoY':
            # Year-over-Year
            # Parse period to get year and month
            year, month = period.split('-')
            prev_year = str(int(year) - 1)
            prev_period = f"{prev_year}-{month}"
            
            # Find previous year's data
            prev_row = None
            for r in filtered_data:
                if r['period'] == prev_period:
                    prev_row = r
                    break
            
            if prev_row is None:
                result['growth_pct'] = 'N/A'
                result['formula'] = 'No data for previous year'
                result['flag'] = 'No previous year data'
            else:
                prev_spend = prev_row['actual_spend']
                if prev_spend is None:
                    result['growth_pct'] = 'N/A'
                    result['formula'] = 'Cannot compute - previous year null'
                    result['flag'] = 'Previous year null'
                else:
                    growth = ((actual_spend - prev_spend) / prev_spend) * 100
                    result['growth_pct'] = f"{growth:+.1f}%"
                    result['formula'] = f"({actual_spend} - {prev_spend}) / {prev_spend} * 100"
        
        results.append(result)
    
    # Write output
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ['period', 'ward', 'category', 'actual_spend', 'growth_pct', 'formula', 'flag']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"Results written to {output_file}")
    print(f"Computed {len(results)} rows")


def main():
    parser = argparse.ArgumentParser(
        description='Calculate budget growth with proper scope and null handling'
    )
    parser.add_argument('--input', required=True, help='Input CSV file')
    parser.add_argument('--ward', required=True, help='Ward name')
    parser.add_argument('--category', required=True, help='Category name')
    parser.add_argument('--growth-type', required=False, help='Growth type: MoM or YoY')
    parser.add_argument('--output', required=True, help='Output CSV file')
    
    args = parser.parse_args()
    
    # Load dataset
    print(f"Loading dataset from {args.input}...")
    dataset = load_dataset(args.input)
    print(f"Loaded {len(dataset['data'])} rows")
    
    # Compute growth
    compute_growth(
        dataset,
        args.ward,
        args.category,
        args.growth_type,
        args.output
    )


if __name__ == '__main__':
    main()
