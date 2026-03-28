"""
UC-0C — Budget Growth Calculator
Computes MoM or YoY growth for specific ward + category combinations.
Builds on RICE principles from agents.md and skills.md.
"""
import argparse
import csv
from typing import Dict, List, Optional


def load_dataset(input_path: str) -> Dict:
    """
    Load ward budget CSV and return data with null count reported.
    """
    required_cols = ['period', 'ward', 'category', 'actual_spend', 'notes']
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Validate columns
            if reader.fieldnames is None:
                raise ValueError("CSV has no headers")
            
            missing = [col for col in required_cols if col not in reader.fieldnames]
            if missing:
                raise ValueError(f"Missing required columns: {missing}")
            
            data = []
            null_rows = []
            
            for row in reader:
                # Track null rows
                if not row.get('actual_spend') or row.get('actual_spend', '').strip() == '':
                    null_rows.append({
                        'period': row['period'],
                        'ward': row['ward'],
                        'category': row['category'],
                        'notes': row.get('notes', '')
                    })
                else:
                    # Parse actual_spend as float
                    row['_actual_spend_num'] = float(row['actual_spend'])
                data.append(row)
            
            return {
                'data': data,
                'null_count': len(null_rows),
                'null_rows': null_rows
            }
    
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {input_path}")


def _get_available_values(data: List[Dict], key: str) -> List[str]:
    """Get unique values for a key from data."""
    return sorted(set(row[key] for row in data))


def compute_growth(data: List[Dict], ward: str, category: str, growth_type: str) -> List[Dict]:
    """
    Compute MoM or YoY growth for ward + category combination.
    """
    # Validate growth type
    growth_type = growth_type.upper()
    if growth_type not in ['MOM', 'YOY']:
        available = 'MoM or YoY'
        raise ValueError(f"Please specify --growth-type {available}")
    
    # Get unique wards and categories
    available_wards = _get_available_values(data, 'ward')
    available_categories = _get_available_values(data, 'category')
    
    # Validate ward
    if ward not in available_wards:
        raise ValueError(f"Ward '{ward}' not found. Available: {', '.join(available_wards)}")
    
    # Validate category
    if category not in available_categories:
        raise ValueError(f"Category '{category}' not found. Available: {', '.join(available_categories)}")
    
    # Filter data for this ward + category
    filtered = [row for row in data if row['ward'] == ward and row['category'] == category]
    
    # Sort by period
    filtered.sort(key=lambda x: x['period'])
    
    # Check minimum periods
    if growth_type == 'MOM' and len(filtered) < 2:
        raise ValueError("Need at least 2 periods for MoM calculation")
    if growth_type == 'YOY' and len(filtered) < 13:
        raise ValueError("Need at least 13 periods (1 year) for YoY calculation")
    
    # Build result
    results = []
    
    for i, row in enumerate(filtered):
        period = row['period']
        actual_spend = row.get('_actual_spend_num')
        notes = row.get('notes', '')
        
        # Handle null values
        if actual_spend is None:
            flag = f"NULL: {notes}" if notes else "NULL: No data"
            results.append({
                'period': period,
                'actual_spend': '',
                'growth_rate': '',
                'formula': '',
                'flag': flag
            })
            continue
        
        # Compute growth
        if growth_type == 'MOM':
            if i == 0:
                # First period - no growth
                results.append({
                    'period': period,
                    'actual_spend': actual_spend,
                    'growth_rate': '',
                    'formula': 'N/A (first period)',
                    'flag': ''
                })
            else:
                # Find previous non-null value
                prev_spend = None
                for j in range(i - 1, -1, -1):
                    if filtered[j].get('_actual_spend_num') is not None:
                        prev_spend = filtered[j]['_actual_spend_num']
                        break
                
                if prev_spend is None:
                    results.append({
                        'period': period,
                        'actual_spend': actual_spend,
                        'growth_rate': '',
                        'formula': 'N/A (no prior data)',
                        'flag': ''
                    })
                else:
                    growth = (actual_spend - prev_spend) / prev_spend * 100
                    formula = f"({actual_spend} - {prev_spend}) / {prev_spend} * 100"
                    results.append({
                        'period': period,
                        'actual_spend': actual_spend,
                        'growth_rate': round(growth, 2),
                        'formula': formula,
                        'flag': ''
                    })
        
        else:  # YoY
            # Find same month last year
            current_month = period[5:7]  # MM from YYYY-MM
            current_year = int(period[:4])
            prev_period = f"{current_year - 1}-{current_month}"
            
            # Find previous year's value
            prev_row = next((r for r in filtered if r['period'] == prev_period), None)
            
            if prev_row is None:
                results.append({
                    'period': period,
                    'actual_spend': actual_spend,
                    'growth_rate': '',
                    'formula': f'N/A (no data for {prev_period})',
                    'flag': ''
                })
            elif prev_row.get('_actual_spend_num') is None:
                results.append({
                    'period': period,
                    'actual_spend': actual_spend,
                    'growth_rate': '',
                    'formula': f'N/A (null for {prev_period})',
                    'flag': f'NULL: {prev_row.get("notes", "No data")}'
                })
            else:
                prev_spend = prev_row['_actual_spend_num']
                growth = (actual_spend - prev_spend) / prev_spend * 100
                formula = f"({actual_spend} - {prev_spend}) / {prev_spend} * 100"
                results.append({
                    'period': period,
                    'actual_spend': actual_spend,
                    'growth_rate': round(growth, 2),
                    'formula': formula,
                    'flag': ''
                })
    
    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name (e.g., 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=True, help="Category name (e.g., 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", required=True, help="Growth type: MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    args = parser.parse_args()
    
    # Refuse if ward or category is "All"
    if args.ward.lower() in ['all', '*']:
        raise ValueError("Refused: Cannot aggregate across all wards. Please specify a specific ward.")
    if args.category.lower() in ['all', '*']:
        raise ValueError("Refused: Cannot aggregate across all categories. Please specify a specific category.")
    
    # Load data
    dataset = load_dataset(args.input)
    
    print(f"Loaded {len(dataset['data'])} rows")
    print(f"Found {dataset['null_count']} null actual_spend values:")
    for null_row in dataset['null_rows']:
        print(f"  - {null_row['period']}, {null_row['ward']}, {null_row['category']}: {null_row['notes'] or 'No notes'}")
    
    # Compute growth
    results = compute_growth(dataset['data'], args.ward, args.category, args.growth_type)
    
    # Write output
    with open(args.output, 'w', encoding='utf-8', newline='') as f:
        if results:
            writer = csv.DictWriter(f, fieldnames=['period', 'actual_spend', 'growth_rate', 'formula', 'flag'])
            writer.writeheader()
            writer.writerows(results)
    
    print(f"\nGrowth data written to {args.output}")
    print(f"Periods computed: {len(results)}")


if __name__ == "__main__":
    main()
