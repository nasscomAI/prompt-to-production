"""
UC-0C app.py — Budget Growth Calculator
Implementation based on RICE framework from agents.md and skills.md.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
import os
from datetime import datetime
from typing import List, Dict, Any


def load_dataset(file_path: str) -> Dict[str, Any]:
    """
    Reads CSV file, validates columns, reports null count and identifies null rows.
    
    Implementation based on skills.md specification.
    Returns: dict with 'data', 'null_count', 'null_rows', 'wards', 'categories'
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Dataset file not found: {file_path}")
    
    required_columns = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Validate columns
            if not reader.fieldnames:
                return {"error": "CSV file has no header row"}
            
            missing_cols = [col for col in required_columns if col not in reader.fieldnames]
            if missing_cols:
                return {"error": f"Missing required columns: {', '.join(missing_cols)}"}
            
            # Load data
            data = []
            null_rows = []
            wards = set()
            categories = set()
            
            for row_num, row in enumerate(reader, start=2):
                # Track unique wards and categories
                if row['ward']:
                    wards.add(row['ward'])
                if row['category']:
                    categories.add(row['category'])
                
                # Check for null actual_spend
                if not row['actual_spend'] or row['actual_spend'].strip() == '':
                    null_rows.append({
                        'row_num': row_num,
                        'period': row['period'],
                        'ward': row['ward'],
                        'category': row['category'],
                        'reason': row.get('notes', 'No reason provided')
                    })
                    row['actual_spend'] = None
                else:
                    try:
                        row['actual_spend'] = float(row['actual_spend'])
                    except ValueError:
                        row['actual_spend'] = None
                
                # Convert budgeted_amount to float
                try:
                    row['budgeted_amount'] = float(row['budgeted_amount'])
                except ValueError:
                    row['budgeted_amount'] = None
                
                data.append(row)
            
            if not data:
                return {"error": "CSV file contains no data rows"}
            
            return {
                'data': data,
                'null_count': len(null_rows),
                'null_rows': null_rows,
                'wards': sorted(list(wards)),
                'categories': sorted(list(categories))
            }
    
    except Exception as e:
        return {"error": f"Error reading CSV file: {e}"}


def compute_growth(dataset_info: Dict[str, Any], ward: str, category: str, growth_type: str) -> List[Dict[str, Any]]:
    """
    Computes period-over-period growth rates for specific ward-category combination.
    
    Implementation based on agents.md enforcement rules and skills.md specification.
    """
    if 'error' in dataset_info:
        return [{"error": dataset_info['error']}]
    
    data = dataset_info['data']
    wards = dataset_info['wards']
    categories = dataset_info['categories']
    
    # Validate ward parameter
    if ward not in wards:
        return [{"error": f"Ward '{ward}' not found. Available wards: {', '.join(wards)}"}]
    
    # Validate category parameter
    if category not in categories:
        return [{"error": f"Category '{category}' not found. Available categories: {', '.join(categories)}"}]
    
    # Validate growth_type parameter
    if growth_type not in ['MoM', 'YoY']:
        return [{"error": f"Invalid growth_type '{growth_type}'. Must be either 'MoM' (Month-over-Month) or 'YoY' (Year-over-Year)."}]
    
    # Filter data for specific ward and category
    filtered_data = [row for row in data if row['ward'] == ward and row['category'] == category]
    
    if not filtered_data:
        return [{"error": f"No data found for ward '{ward}' and category '{category}'"}]
    
    # Sort by period
    filtered_data.sort(key=lambda x: x['period'])
    
    if len(filtered_data) < 2:
        return [{"error": f"Insufficient data for growth calculation. Found only {len(filtered_data)} period(s). Need at least 2 periods."}]
    
    # Compute growth for each period
    results = []
    
    for i, row in enumerate(filtered_data):
        period = row['period']
        actual_spend = row['actual_spend']
        
        result = {
            'period': period,
            'actual_spend': actual_spend if actual_spend is not None else 'NULL',
            'growth_rate': None,
            'formula': None,
            'null_reason': ''
        }
        
        # Handle null actual_spend
        if actual_spend is None:
            result['growth_rate'] = 'NULL_FLAGGED'
            result['formula'] = 'Cannot compute - actual_spend is NULL'
            result['null_reason'] = row.get('notes', 'No reason provided')
            results.append(result)
            continue
        
        # Compute growth based on type
        if growth_type == 'MoM':
            # Month-over-Month: compare with previous month
            if i == 0:
                result['growth_rate'] = 'N/A (first period)'
                result['formula'] = 'MoM: (current - previous) / previous * 100'
            else:
                prev_row = filtered_data[i - 1]
                prev_spend = prev_row['actual_spend']
                
                if prev_spend is None:
                    result['growth_rate'] = 'N/A (previous period is NULL)'
                    result['formula'] = 'MoM: Cannot compute due to NULL in previous period'
                elif prev_spend == 0:
                    result['growth_rate'] = 'N/A (division by zero)'
                    result['formula'] = 'MoM: Cannot compute (previous period = 0)'
                else:
                    growth = ((actual_spend - prev_spend) / prev_spend) * 100
                    result['growth_rate'] = f"{growth:+.1f}%"
                    result['formula'] = f"MoM: ({actual_spend} - {prev_spend}) / {prev_spend} * 100"
        
        elif growth_type == 'YoY':
            # Year-over-Year: compare with same month last year (12 months ago)
            # Find row from 12 months prior
            current_year, current_month = period.split('-')
            target_year = str(int(current_year) - 1)
            target_period = f"{target_year}-{current_month}"
            
            year_ago_row = next((r for r in filtered_data if r['period'] == target_period), None)
            
            if year_ago_row is None:
                result['growth_rate'] = 'N/A (no data from year ago)'
                result['formula'] = f"YoY: No data for period {target_period}"
            else:
                year_ago_spend = year_ago_row['actual_spend']
                
                if year_ago_spend is None:
                    result['growth_rate'] = 'N/A (year ago period is NULL)'
                    result['formula'] = f"YoY: Cannot compute due to NULL in {target_period}"
                elif year_ago_spend == 0:
                    result['growth_rate'] = 'N/A (division by zero)'
                    result['formula'] = f"YoY: Cannot compute (year ago period = 0)"
                else:
                    growth = ((actual_spend - year_ago_spend) / year_ago_spend) * 100
                    result['growth_rate'] = f"{growth:+.1f}%"
                    result['formula'] = f"YoY: ({actual_spend} - {year_ago_spend}) / {year_ago_spend} * 100"
        
        results.append(result)
    
    return results


def main():
    """
    Main function to process budget data and compute growth rates.
    """
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv file")
    parser.add_argument("--ward", required=True, help="Specific ward name (e.g., 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=True, help="Specific category name (e.g., 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", required=True, choices=['MoM', 'YoY'], 
                        help="Growth type: MoM (Month-over-Month) or YoY (Year-over-Year)")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()
    
    try:
        # Load dataset
        print(f"Loading dataset from: {args.input}")
        dataset_info = load_dataset(args.input)
        
        if 'error' in dataset_info:
            print(f"ERROR: {dataset_info['error']}")
            return
        
        print(f"Dataset loaded: {len(dataset_info['data'])} rows")
        print(f"Found {len(dataset_info['wards'])} wards and {len(dataset_info['categories'])} categories")
        
        # Report null values
        if dataset_info['null_count'] > 0:
            print(f"\nWARNING: Found {dataset_info['null_count']} NULL actual_spend values:")
            for null_row in dataset_info['null_rows']:
                print(f"  - Row {null_row['row_num']}: {null_row['period']} | {null_row['ward']} | {null_row['category']}")
                print(f"    Reason: {null_row['reason']}")
        else:
            print("No NULL values found in actual_spend column")
        
        # Compute growth
        print(f"\nComputing {args.growth_type} growth for:")
        print(f"  Ward: {args.ward}")
        print(f"  Category: {args.category}")
        
        results = compute_growth(dataset_info, args.ward, args.category, args.growth_type)
        
        if results and 'error' in results[0]:
            print(f"ERROR: {results[0]['error']}")
            return
        
        # Write results to CSV
        with open(args.output, 'w', encoding='utf-8', newline='') as f:
            fieldnames = ['period', 'actual_spend', 'growth_rate', 'formula', 'null_reason']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        
        print(f"\nDone. Results written to {args.output}")
        print(f"Processed {len(results)} periods")
        
        # Summary statistics
        null_flagged = sum(1 for r in results if r['growth_rate'] == 'NULL_FLAGGED')
        computed = sum(1 for r in results if r['growth_rate'] not in ['NULL_FLAGGED', 'N/A (first period)', 'N/A (previous period is NULL)', 'N/A (no data from year ago)', 'N/A (year ago period is NULL)', 'N/A (division by zero)'] and r['growth_rate'] is not None)
        
        print(f"Summary: {computed} growth rates computed, {null_flagged} NULL values flagged")
        
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}")


if __name__ == "__main__":
    main()
