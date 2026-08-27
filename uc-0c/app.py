"""
UC-0C app.py — Budget Growth Analysis with Null Awareness
Implements RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any


def load_dataset(file_path: str) -> Optional[Dict]:
    """
    Skill: load_dataset
    Reads CSV, validates columns, identifies and reports null actual_spend values.
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        Dictionary with data, null_count, null_details, wards, categories, periods
    """
    try:
        path = Path(file_path)
        if not path.exists():
            print(f"ERROR: File not found: {file_path}", file=sys.stderr)
            return None
            
        if not path.is_file():
            print(f"ERROR: Path is not a file: {file_path}", file=sys.stderr)
            return None
            
        # Read CSV
        data = []
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Validate required columns
            required_columns = {'period', 'ward', 'category', 'budgeted_amount', 
                              'actual_spend', 'notes'}
            if not required_columns.issubset(set(reader.fieldnames or [])):
                missing = required_columns - set(reader.fieldnames or [])
                print(f"ERROR: Missing required columns: {missing}", file=sys.stderr)
                return None
                
            for row in reader:
                data.append(row)
                
        if not data:
            print(f"ERROR: CSV file is empty: {file_path}", file=sys.stderr)
            return None
            
        # Identify null actual_spend values
        null_details = []
        for row in data:
            if not row['actual_spend'] or row['actual_spend'].strip() == '':
                null_details.append({
                    'period': row['period'],
                    'ward': row['ward'],
                    'category': row['category'],
                    'reason': row['notes'].strip() if row['notes'] else 'No reason provided'
                })
                
        # Extract unique values
        wards = sorted(list(set(row['ward'] for row in data)))
        categories = sorted(list(set(row['category'] for row in data)))
        periods = sorted(list(set(row['period'] for row in data)))
        
        return {
            'data': data,
            'null_count': len(null_details),
            'null_details': null_details,
            'wards': wards,
            'categories': categories,
            'periods': periods
        }
        
    except Exception as e:
        print(f"ERROR: Failed to load dataset: {str(e)}", file=sys.stderr)
        return None


def compute_growth(dataset: Dict, ward: str, category: str, 
                   growth_type: str) -> Optional[List[Dict]]:
    """
    Skill: compute_growth
    Computes growth metrics for specific ward and category.
    
    Args:
        dataset: Dictionary from load_dataset
        ward: Specific ward name
        category: Specific category name
        growth_type: 'MoM' or 'YoY'
        
    Returns:
        List of dictionaries with period, actual_spend, growth_value, formula_used, note
    """
    # Validate growth_type
    if growth_type not in ['MoM', 'YoY']:
        print(f"ERROR: growth_type must be 'MoM' or 'YoY', got: {growth_type}", 
              file=sys.stderr)
        return None
        
    # Validate ward and category
    if ward not in dataset['wards']:
        print(f"ERROR: Ward '{ward}' not found in dataset.", file=sys.stderr)
        print(f"Available wards: {', '.join(dataset['wards'])}", file=sys.stderr)
        return None
        
    if category not in dataset['categories']:
        print(f"ERROR: Category '{category}' not found in dataset.", file=sys.stderr)
        print(f"Available categories: {', '.join(dataset['categories'])}", file=sys.stderr)
        return None
        
    # Filter data for specified ward and category
    filtered_data = [
        row for row in dataset['data']
        if row['ward'] == ward and row['category'] == category
    ]
    
    # Sort by period
    filtered_data = sorted(filtered_data, key=lambda x: x['period'])
    
    # Build null lookup
    null_lookup = {
        (nd['period'], nd['ward'], nd['category']): nd['reason']
        for nd in dataset['null_details']
    }
    
    # Compute growth
    results = []
    
    for i, row in enumerate(filtered_data):
        period = row['period']
        actual_spend_str = row['actual_spend'].strip() if row['actual_spend'] else ''
        
        # Check if current period has null
        null_key = (period, ward, category)
        if null_key in null_lookup:
            results.append({
                'period': period,
                'actual_spend': 'NULL',
                'growth_value': 'NULL_FLAGGED',
                'formula_used': 'N/A',
                'note': f"Null value: {null_lookup[null_key]}"
            })
            continue
            
        # Parse actual_spend
        try:
            current_spend = float(actual_spend_str)
        except ValueError:
            results.append({
                'period': period,
                'actual_spend': actual_spend_str,
                'growth_value': 'ERROR',
                'formula_used': 'N/A',
                'note': 'Invalid actual_spend value'
            })
            continue
            
        # Compute growth based on type
        if growth_type == 'MoM':
            # Month-over-Month
            if i == 0:
                # First period has no previous month
                results.append({
                    'period': period,
                    'actual_spend': f"{current_spend}",
                    'growth_value': 'N/A',
                    'formula_used': 'N/A',
                    'note': 'First period - no previous month for comparison'
                })
            else:
                # Get previous month
                prev_row = filtered_data[i - 1]
                prev_spend_str = prev_row['actual_spend'].strip() if prev_row['actual_spend'] else ''
                
                # Check if previous period has null
                prev_null_key = (prev_row['period'], ward, category)
                if prev_null_key in null_lookup:
                    results.append({
                        'period': period,
                        'actual_spend': f"{current_spend}",
                        'growth_value': 'NULL_FLAGGED',
                        'formula_used': 'N/A',
                        'note': f"Previous period null: {null_lookup[prev_null_key]}"
                    })
                    continue
                    
                try:
                    prev_spend = float(prev_spend_str)
                    if prev_spend == 0:
                        growth_pct = 'INFINITE' if current_spend > 0 else 'N/A'
                        formula = f"MoM = ({current_spend} - {prev_spend}) / {prev_spend} × 100%"
                        note = 'Previous spend was zero - division by zero'
                    else:
                        growth_pct = ((current_spend - prev_spend) / prev_spend) * 100
                        formula = f"MoM = ({current_spend} - {prev_spend}) / {prev_spend} × 100%"
                        note = ''
                        
                    results.append({
                        'period': period,
                        'actual_spend': f"{current_spend}",
                        'growth_value': f"{growth_pct:.1f}%" if isinstance(growth_pct, float) else growth_pct,
                        'formula_used': formula,
                        'note': note
                    })
                except ValueError:
                    results.append({
                        'period': period,
                        'actual_spend': f"{current_spend}",
                        'growth_value': 'ERROR',
                        'formula_used': 'N/A',
                        'note': 'Invalid previous period value'
                    })
                    
        elif growth_type == 'YoY':
            # Year-over-Year
            # For YoY in 2024 data, we don't have 2023 data, so all will be N/A
            results.append({
                'period': period,
                'actual_spend': f"{current_spend}",
                'growth_value': 'N/A',
                'formula_used': 'N/A',
                'note': 'YoY requires previous year data - not available in dataset'
            })
            
    return results


def main():
    """
    Main application entry point.
    Orchestrates dataset loading and growth computation with enforcement rules.
    """
    parser = argparse.ArgumentParser(
        description='UC-0C: Budget Growth Analysis with Null Awareness',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example:
  python app.py --input ../data/budget/ward_budget.csv \\
    --ward "Ward 1 – Kasba" \\
    --category "Roads & Pothole Repair" \\
    --growth-type MoM \\
    --output growth_output.csv
        """
    )
    
    parser.add_argument(
        '--input',
        required=True,
        help='Path to input CSV file with ward budget data'
    )
    
    parser.add_argument(
        '--ward',
        required=True,
        help='Specific ward name (must match exactly)'
    )
    
    parser.add_argument(
        '--category',
        required=True,
        help='Specific category name (must match exactly)'
    )
    
    parser.add_argument(
        '--growth-type',
        required=True,
        choices=['MoM', 'YoY'],
        help='Growth type: MoM (Month-over-Month) or YoY (Year-over-Year)'
    )
    
    parser.add_argument(
        '--output',
        required=True,
        help='Path to output CSV file'
    )
    
    args = parser.parse_args()
    
    # Step 1: Load dataset using load_dataset skill
    print(f"Loading dataset: {args.input}")
    dataset = load_dataset(args.input)
    
    if dataset is None:
        print("ERROR: Failed to load dataset", file=sys.stderr)
        sys.exit(1)
        
    print(f"Dataset loaded: {len(dataset['data'])} rows")
    print(f"Wards: {len(dataset['wards'])}, Categories: {len(dataset['categories'])}, "
          f"Periods: {len(dataset['periods'])}")
    
    # Report null values upfront
    print(f"\nNull actual_spend values found: {dataset['null_count']}")
    if dataset['null_count'] > 0:
        print("Null details:")
        for nd in dataset['null_details']:
            print(f"  • {nd['period']} | {nd['ward']} | {nd['category']}")
            print(f"    Reason: {nd['reason']}")
    
    # Step 2: Compute growth using compute_growth skill
    print(f"\nComputing {args.growth_type} growth for:")
    print(f"  Ward: {args.ward}")
    print(f"  Category: {args.category}")
    
    results = compute_growth(
        dataset=dataset,
        ward=args.ward,
        category=args.category,
        growth_type=args.growth_type
    )
    
    if results is None:
        print("ERROR: Failed to compute growth", file=sys.stderr)
        sys.exit(1)
        
    # Step 3: Write results to CSV
    try:
        output_path = Path(args.output)
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['period', 'actual_spend', 'growth_value', 'formula_used', 'note']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
        print(f"\nResults written to: {args.output}")
        print(f"Total periods: {len(results)}")
        
        # Summary statistics
        computable = [r for r in results if r['growth_value'] not in 
                     ['N/A', 'NULL_FLAGGED', 'ERROR', 'INFINITE']]
        print(f"Computable growth values: {len(computable)}")
        
        null_flagged = [r for r in results if r['growth_value'] == 'NULL_FLAGGED']
        if null_flagged:
            print(f"Periods with null values: {len(null_flagged)}")
            
    except Exception as e:
        print(f"ERROR: Failed to write output file: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
