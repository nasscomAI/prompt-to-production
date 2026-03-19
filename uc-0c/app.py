"""
UC-0C — Budget Growth Calculator
Built using RICE + agents.md + skills.md + CRAFT workflow.
Computes growth metrics for single ward-category combinations with null handling and formula display.
"""
import argparse
import csv
from typing import Dict, List, Optional


def load_dataset(file_path: str) -> Dict:
    """
    Reads ward budget CSV file, validates columns, and reports null actual_spend values.
    
    Args:
        file_path: Path to CSV file
        
    Returns:
        Dictionary with 'data' (list of row dicts) and 'null_report' (null count and details)
        
    Raises:
        FileNotFoundError: If file does not exist or is not readable
        ValueError: If required columns missing or CSV malformed
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            required_columns = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
            
            if not reader.fieldnames:
                raise ValueError("CSV file is empty or has no headers")
            
            missing_columns = [col for col in required_columns if col not in reader.fieldnames]
            if missing_columns:
                raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
            
            data = list(reader)
            
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {file_path}")
    except csv.Error as e:
        raise ValueError(f"CSV is malformed: {e}")
    
    if not data:
        raise ValueError("CSV file contains no data rows")
    
    # Report null actual_spend values
    null_rows = []
    for row in data:
        if not row['actual_spend'] or row['actual_spend'].strip() == '':
            null_rows.append({
                'period': row['period'],
                'ward': row['ward'],
                'category': row['category'],
                'reason': row['notes']
            })
    
    null_report = {
        'null_count': len(null_rows),
        'null_rows': null_rows
    }
    
    return {
        'data': data,
        'null_report': null_report
    }


def compute_growth(data: List[Dict], ward: str, category: str, growth_type: str) -> Dict:
    """
    Computes growth (MoM or YoY) for specified ward-category with output matching README format.
    
    Args:
        data: List of row dictionaries from load_dataset
        ward: Exact ward name to filter
        category: Exact category name to filter
        growth_type: 'MoM' or 'YoY'
        
    Returns:
        Dictionary with 'results' (list with Ward, Category, Period, Actual Spend, Growth columns) and 'metadata'
        
    Raises:
        ValueError: If ward/category don't exist, growth_type invalid, or no data found
    """
    # Validate growth_type
    if growth_type not in ['MoM', 'YoY']:
        raise ValueError("growth_type must be MoM or YoY")
    
    # Get all unique wards and categories for validation
    all_wards = sorted(set(row['ward'] for row in data))
    all_categories = sorted(set(row['category'] for row in data))
    
    if ward not in all_wards:
        raise ValueError(f"Ward '{ward}' not found. Valid wards: {', '.join(all_wards)}")
    
    if category not in all_categories:
        raise ValueError(f"Category '{category}' not found. Valid categories: {', '.join(all_categories)}")
    
    # Filter to ward and category
    filtered_data = [row for row in data if row['ward'] == ward and row['category'] == category]
    
    if not filtered_data:
        raise ValueError(f"No data found for ward='{ward}' and category='{category}'")
    
    # Sort by period
    filtered_data.sort(key=lambda x: x['period'])
    
    results = []
    calculable_periods = 0
    growth_column_name = 'MoM Growth' if growth_type == 'MoM' else 'YoY Growth'
    
    for i, row in enumerate(filtered_data):
        period = row['period']
        actual_spend_str = row['actual_spend'].strip() if row['actual_spend'] else ''
        
        result = {
            'Ward': ward,
            'Category': category,
            'Period': period,
            'Actual Spend (₹ lakh)': 'NULL' if not actual_spend_str else actual_spend_str,
            growth_column_name: ''
        }
        
        # Check if current value is null
        if not actual_spend_str:
            result[growth_column_name] = f"NULL - {row['notes']}"
            results.append(result)
            continue
        
        current_value = float(actual_spend_str)
        
        # Compute growth based on type
        if growth_type == 'MoM':
            if i == 0:
                result[growth_column_name] = 'N/A - no prior period'
            else:
                prev_row = filtered_data[i - 1]
                prev_spend_str = prev_row['actual_spend'].strip() if prev_row['actual_spend'] else ''
                
                if not prev_spend_str:
                    result[growth_column_name] = f"Cannot compute - previous period NULL ({prev_row['notes']})"
                else:
                    prev_value = float(prev_spend_str)
                    growth = ((current_value - prev_value) / prev_value) * 100
                    # Use minus sign (−) not hyphen for negative
                    sign = '+' if growth >= 0 else '−'
                    result[growth_column_name] = f"{sign}{abs(growth):.1f}%"
                    calculable_periods += 1
        
        elif growth_type == 'YoY':
            # For YoY, need same month from previous year
            current_year = int(period.split('-')[0])
            current_month = period.split('-')[1]
            prior_year_period = f"{current_year - 1}-{current_month}"
            
            # Find prior year row
            prior_year_row = next((r for r in filtered_data if r['period'] == prior_year_period), None)
            
            if not prior_year_row:
                result[growth_column_name] = 'N/A - no prior year data'
            else:
                prior_spend_str = prior_year_row['actual_spend'].strip() if prior_year_row['actual_spend'] else ''
                
                if not prior_spend_str:
                    result[growth_column_name] = f"Cannot compute - prior year period NULL ({prior_year_row['notes']})"
                else:
                    prior_value = float(prior_spend_str)
                    growth = ((current_value - prior_value) / prior_value) * 100
                    # Use minus sign (−) not hyphen for negative
                    sign = '+' if growth >= 0 else '−'
                    result[growth_column_name] = f"{sign}{abs(growth):.1f}%"
                    calculable_periods += 1
        
        results.append(result)
    
    metadata = {
        'ward': ward,
        'category': category,
        'growth_type': growth_type,
        'total_periods': len(results),
        'calculable_periods': calculable_periods
    }
    
    return {
        'results': results,
        'metadata': metadata
    }


def main():
    """
    Main entry point for budget growth calculator.
    """
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Exact ward name (e.g., 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=True, help="Exact category name (e.g., 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", required=True, help="Growth calculation type: MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()
    
    try:
        # Load dataset
        print(f"Loading dataset: {args.input}")
        dataset = load_dataset(args.input)
        
        # Report null values
        null_report = dataset['null_report']
        print(f"\nNull Value Report:")
        print(f"  Total null actual_spend values: {null_report['null_count']}")
        if null_report['null_count'] > 0:
            print(f"  Null rows:")
            for null_row in null_report['null_rows']:
                print(f"    - {null_row['period']} · {null_row['ward']} · {null_row['category']}")
                print(f"      Reason: {null_row['reason']}")
        print()
        
        # Compute growth
        print(f"Computing {args.growth_type} growth for:")
        print(f"  Ward: {args.ward}")
        print(f"  Category: {args.category}")
        
        growth_results = compute_growth(
            dataset['data'],
            args.ward,
            args.category,
            args.growth_type
        )
        
        # Write output
        growth_column_name = 'MoM Growth' if args.growth_type == 'MoM' else 'YoY Growth'
        with open(args.output, 'w', encoding='utf-8', newline='') as f:
            fieldnames = ['Ward', 'Category', 'Period', 'Actual Spend (₹ lakh)', growth_column_name]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            writer.writeheader()
            writer.writerows(growth_results['results'])
        
        # Print summary
        metadata = growth_results['metadata']
        print(f"\nResults written to: {args.output}")
        print(f"  Total periods: {metadata['total_periods']}")
        print(f"  Calculable periods: {metadata['calculable_periods']}")
        print(f"  Uncalculable periods: {metadata['total_periods'] - metadata['calculable_periods']}")
        print("\n✓ Growth calculations complete")
        print("✓ Ward and Category columns included in every row")
        print("✓ Null values flagged with reasons")
        
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
        exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
