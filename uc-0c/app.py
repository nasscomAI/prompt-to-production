"""
UC-0C — Number That Looks Right
Built using RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import sys
import os
import csv
from datetime import datetime

def load_dataset(input_path: str) -> dict:
    """
    Reads budget CSV, validates columns, reports null count and which rows.
    
    Implements skills.md load_dataset specification:
    - Validates required columns present
    - Identifies all null actual_spend values
    - Reports null rows with reasons before returning
    """
    # Error handling: Check if file exists
    if not os.path.exists(input_path):
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    
    # Read CSV
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = list(reader)
    except Exception as e:
        print(f"Error: Failed to read CSV file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Error handling: Validate required columns
    required_columns = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
    if data:
        missing_columns = [col for col in required_columns if col not in data[0].keys()]
        if missing_columns:
            print(f"Error: Missing required columns: {', '.join(missing_columns)}", file=sys.stderr)
            sys.exit(1)
    
    # Identify null actual_spend rows (enforcement rule 2)
    null_rows = []
    for row in data:
        if not row['actual_spend'] or row['actual_spend'].strip() == '':
            null_rows.append({
                'period': row['period'],
                'ward': row['ward'],
                'category': row['category'],
                'reason': row['notes'].strip() if row['notes'] else 'No reason provided'
            })
    
    # Get unique wards and categories
    wards = sorted(list(set(row['ward'] for row in data)))
    categories = sorted(list(set(row['category'] for row in data)))
    
    # Report null rows (enforcement rule 2: flag every null before computing)
    print("\n" + "="*70)
    print("NULL VALUE REPORT")
    print("="*70)
    print(f"Total rows: {len(data)}")
    print(f"Null actual_spend rows: {len(null_rows)}")
    if null_rows:
        print("\nNull rows details:")
        for null_row in null_rows:
            print(f"  - {null_row['period']} · {null_row['ward']} · {null_row['category']}")
            print(f"    Reason: {null_row['reason']}")
    else:
        print("  No null values found")
    print("="*70)
    print()
    
    return {
        'data': data,
        'null_rows': null_rows,
        'null_count': len(null_rows),
        'wards': wards,
        'categories': categories
    }


def compute_growth(dataset: dict, ward: str, category: str, growth_type: str, output_path: str):
    """
    Computes period-over-period growth for specific ward-category combination.
    
    Implements skills.md compute_growth specification:
    - Shows formula for each calculation
    - Flags null periods
    - Returns per-period table, not single number
    - Refuses if growth_type not specified
    """
    data = dataset['data']
    wards = dataset['wards']
    categories = dataset['categories']
    null_rows = dataset['null_rows']
    
    # Error handling: Validate ward exists (enforcement rule 6)
    if ward not in wards:
        print(f"Error: Ward '{ward}' not found in dataset.", file=sys.stderr)
        print(f"Available wards: {', '.join(wards)}", file=sys.stderr)
        sys.exit(1)
    
    # Error handling: Validate category exists (enforcement rule 6)
    if category not in categories:
        print(f"Error: Category '{category}' not found in dataset.", file=sys.stderr)
        print(f"Available categories: {', '.join(categories)}", file=sys.stderr)
        sys.exit(1)
    
    # Error handling: Validate growth_type (enforcement rule 4)
    if not growth_type or growth_type not in ['MoM', 'YoY']:
        print(f"Error: --growth-type must be specified as either MoM (Month-over-Month) or YoY (Year-over-Year).", file=sys.stderr)
        print(f"Cannot assume growth calculation method.", file=sys.stderr)
        sys.exit(1)
    
    # Filter data for specific ward-category combination (enforcement rule 1)
    filtered_data = [row for row in data if row['ward'] == ward and row['category'] == category]
    
    # Error handling: Check if data exists for combination
    if not filtered_data:
        print(f"Error: No data found for Ward '{ward}' and Category '{category}'", file=sys.stderr)
        sys.exit(1)
    
    # Sort by period
    filtered_data.sort(key=lambda x: x['period'])
    
    # Prepare output
    results = []
    
    print(f"\nComputing {growth_type} growth for:")
    print(f"  Ward: {ward}")
    print(f"  Category: {category}")
    print(f"  Growth Type: {growth_type}")
    print()
    
    # Compute growth for each period (enforcement rule 3: show formula)
    for i, row in enumerate(filtered_data):
        period = row['period']
        actual_spend = row['actual_spend'].strip() if row['actual_spend'] else None
        
        # Check if current period has null value (enforcement rule 2)
        is_null = not actual_spend or actual_spend == ''
        
        if is_null:
            # Find reason from null_rows
            reason = next((nr['reason'] for nr in null_rows 
                          if nr['period'] == period and nr['ward'] == ward and nr['category'] == category), 
                         'No reason provided')
            
            results.append({
                'period': period,
                'actual_spend': 'NULL',
                'growth_percentage': 'CANNOT COMPUTE',
                'formula_used': f'NULL - CANNOT COMPUTE: {reason}',
                'notes': reason
            })
            print(f"Period {period}: NULL - CANNOT COMPUTE: {reason}")
            continue
        
        current_value = float(actual_spend)
        
        if i == 0:
            # First period - no previous to compare
            results.append({
                'period': period,
                'actual_spend': f"{current_value}",
                'growth_percentage': 'N/A',
                'formula_used': 'N/A - no previous period',
                'notes': 'First period'
            })
            print(f"Period {period}: ₹{current_value} lakh (First period - no growth calculation)")
        else:
            # Get previous period value
            if growth_type == 'MoM':
                # Month-over-Month: compare with previous month
                prev_row = filtered_data[i-1]
            else:  # YoY
                # Year-over-Year: compare with same month last year (12 months ago)
                # For simplicity in this dataset, we'll look for period 12 months back
                prev_period_year = int(period[:4]) - 1
                prev_period_month = period[5:7]
                prev_period_str = f"{prev_period_year}-{prev_period_month}"
                prev_row = next((r for r in filtered_data if r['period'] == prev_period_str), None)
                
                if not prev_row:
                    results.append({
                        'period': period,
                        'actual_spend': f"{current_value}",
                        'growth_percentage': 'N/A',
                        'formula_used': 'N/A - no data for same period last year',
                        'notes': 'Insufficient historical data for YoY'
                    })
                    print(f"Period {period}: ₹{current_value} lakh (No YoY comparison data)")
                    continue
            
            prev_actual_spend = prev_row['actual_spend'].strip() if prev_row['actual_spend'] else None
            is_prev_null = not prev_actual_spend or prev_actual_spend == ''
            
            if is_prev_null:
                # Previous period is null - cannot compute growth
                results.append({
                    'period': period,
                    'actual_spend': f"{current_value}",
                    'growth_percentage': 'CANNOT COMPUTE',
                    'formula_used': f'CANNOT COMPUTE - previous period ({prev_row["period"]}) is null',
                    'notes': 'Previous period null'
                })
                print(f"Period {period}: ₹{current_value} lakh - CANNOT COMPUTE (previous period null)")
            else:
                prev_value = float(prev_actual_spend)
                
                # Calculate growth (enforcement rule 3: show exact formula)
                growth = ((current_value - prev_value) / prev_value) * 100
                formula = f"({current_value} - {prev_value}) / {prev_value} * 100 = {growth:+.1f}%"
                
                results.append({
                    'period': period,
                    'actual_spend': f"{current_value}",
                    'growth_percentage': f"{growth:+.1f}%",
                    'formula_used': formula,
                    'notes': ''
                })
                print(f"Period {period}: ₹{current_value} lakh, Growth: {formula}")
    
    # Write output CSV (enforcement rule 5: per-period table)
    try:
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            fieldnames = ['period', 'actual_spend', 'growth_percentage', 'formula_used', 'notes']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        
        print(f"\n✓ Output written to: {output_path}")
        print(f"  Total periods: {len(results)}")
        print(f"  Computed growth: {sum(1 for r in results if r['growth_percentage'] not in ['N/A', 'CANNOT COMPUTE'])}")
        print(f"  Null periods: {sum(1 for r in results if r['actual_spend'] == 'NULL')}")
        
    except Exception as e:
        print(f"Error: Failed to write output file: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """
    Main entry point implementing UC-0C workflow.
    Accepts command line arguments as specified in UC README.
    """
    parser = argparse.ArgumentParser(
        description="UC-0C — Number That Looks Right: Budget Growth Calculator"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to budget CSV file (e.g., ../data/budget/ward_budget.csv)"
    )
    parser.add_argument(
        "--ward",
        required=True,
        help="Ward name (e.g., 'Ward 1 – Kasba')"
    )
    parser.add_argument(
        "--category",
        required=True,
        help="Budget category (e.g., 'Roads & Pothole Repair')"
    )
    parser.add_argument(
        "--growth-type",
        required=True,
        choices=['MoM', 'YoY'],
        help="Growth calculation type: MoM (Month-over-Month) or YoY (Year-over-Year)"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to write growth output CSV (e.g., growth_output.csv)"
    )
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("UC-0C: Budget Growth Calculator")
    print("=" * 70)
    print(f"Input: {args.input}")
    print(f"Ward: {args.ward}")
    print(f"Category: {args.category}")
    print(f"Growth Type: {args.growth_type}")
    print(f"Output: {args.output}")
    
    # Step 1: Load dataset with null reporting (implements load_dataset skill)
    dataset = load_dataset(args.input)
    
    # Step 2: Compute growth (implements compute_growth skill)
    compute_growth(dataset, args.ward, args.category, args.growth_type, args.output)
    
    print("\n" + "=" * 70)
    print("Done. Growth calculation completed with all enforcement rules applied.")
    print("=" * 70)


if __name__ == "__main__":
    main()

