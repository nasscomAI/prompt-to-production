"""
UC-0C — Number That Looks Right (Growth Analysis)
Implementation guided by RICE framework, agents.md, and skills.md.
"""
import argparse
import csv
import os
import sys

def load_dataset(file_path: str):
    """
    Reads the ward budget CSV, validates columns, and explicitly reports null rows.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input file not found: {file_path}")
        
    required_cols = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
    data = []
    null_rows = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        # Validate columns
        if not required_cols.issubset(set(reader.fieldnames or [])):
            missing = required_cols - set(reader.fieldnames or [])
            raise ValueError(f"Missing required columns: {missing}. Halting execution.")
            
        for row in reader:
            data.append(row)
            spend = row.get('actual_spend', '').strip()
            if not spend:
                null_rows.append({
                    'period': row['period'],
                    'ward': row['ward'],
                    'category': row['category'],
                    'null_reason': row.get('notes', 'No reason provided')
                })
                
    # Report nulls explicitly as required by error handling
    print(f"Dataset loaded. Found {len(null_rows)} null actual_spend rows:")
    for nr in null_rows:
        print(f"  - {nr['period']} | {nr['ward']} | {nr['category']} | Reason: {nr['null_reason']}")
        
    return data, null_rows


def compute_growth(filtered_data: list, growth_type: str):
    """
    Computes per-period growth for a strictly filtered single-ward, single-category dataset.
    """
    if not growth_type or growth_type not in ["MoM", "YoY"]:
        raise ValueError("REFUSE: --growth-type must be specified explicitly as exactly 'MoM' or 'YoY'. Never guess.")
        
    if not filtered_data:
        return []
        
    # Validate strictly scoped (no cross-aggregation)
    wards = set(row['ward'] for row in filtered_data)
    categories = set(row['category'] for row in filtered_data)
    
    if len(wards) > 1 or len(categories) > 1:
        raise ValueError("REFUSE: Dataset contains rows from more than one ward or category. Cross-aggregation is prohibited.")
        
    # Sort chronologically
    sorted_data = sorted(filtered_data, key=lambda x: x['period'])
    results = []
    
    for i, row in enumerate(sorted_data):
        period = row['period']
        spend_str = row.get('actual_spend', '').strip()
        
        if not spend_str:
            results.append({
                'period': period,
                'actual_spend': 'NULL',
                'growth_value': 'NULL',
                'formula': f"Not computed: {row.get('notes', 'Unknown reason')}"
            })
            continue
            
        current_spend = float(spend_str)
        
        if growth_type == "MoM":
            # Previous month is just i-1 if it exists and is contiguous
            # Assuming strictly monthly data here for MoM
            if i == 0:
                results.append({
                    'period': period,
                    'actual_spend': current_spend,
                    'growth_value': 'N/A',
                    'formula': 'N/A (first period)'
                })
            else:
                prev_row = sorted_data[i-1]
                prev_spend_str = prev_row.get('actual_spend', '').strip()
                if not prev_spend_str:
                    results.append({
                        'period': period,
                        'actual_spend': current_spend,
                        'growth_value': 'N/A',
                        'formula': 'Cannot compute MoM: Previous month is NULL'
                    })
                else:
                    prev_spend = float(prev_spend_str)
                    if prev_spend == 0:
                        results.append({
                            'period': period,
                            'actual_spend': current_spend,
                            'growth_value': 'N/A',
                            'formula': 'Cannot compute MoM: Previous month is 0 (divide by zero)'
                        })
                    else:
                        growth = (current_spend - prev_spend) / prev_spend * 100
                        # Formatting to match the README reference values visually (+33.1%)
                        sign = "+" if growth > 0 else ""
                        formatted_growth = f"{sign}{growth:.1f}%"
                        results.append({
                            'period': period,
                            'actual_spend': current_spend,
                            'growth_value': formatted_growth,
                            'formula': f"MoM: ({current_spend} - {prev_spend}) / {prev_spend} * 100"
                        })
        elif growth_type == "YoY":
            # For YoY, we look 12 months back. If index < 12, we can't compute YoY.
            if i < 12:
                results.append({
                    'period': period,
                    'actual_spend': current_spend,
                    'growth_value': 'N/A',
                    'formula': 'N/A (insufficient history for YoY)'
                })
            else:
                prev_row = sorted_data[i-12]
                prev_spend_str = prev_row.get('actual_spend', '').strip()
                if not prev_spend_str:
                    results.append({
                        'period': period,
                        'actual_spend': current_spend,
                        'growth_value': 'N/A',
                        'formula': 'Cannot compute YoY: Previous year is NULL'
                    })
                else:
                    prev_spend = float(prev_spend_str)
                    if prev_spend == 0:
                        results.append({
                            'period': period,
                            'actual_spend': current_spend,
                            'growth_value': 'N/A',
                            'formula': 'Cannot compute YoY: Previous year is 0 (divide by zero)'
                        })
                    else:
                        growth = (current_spend - prev_spend) / prev_spend * 100
                        sign = "+" if growth > 0 else ""
                        formatted_growth = f"{sign}{growth:.1f}%"
                        results.append({
                            'period': period,
                            'actual_spend': current_spend,
                            'growth_value': formatted_growth,
                            'formula': f"YoY: ({current_spend} - {prev_spend}) / {prev_spend} * 100"
                        })
                        
    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Specific ward to analyze (e.g. 'Ward 1 - Kasba')")
    parser.add_argument("--category", required=True, help="Specific category to analyze")
    # Growth type is intentionally not defaulted to enforce Rule 4
    parser.add_argument("--growth-type", required=False, help="Must be MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    
    args = parser.parse_args()
    
    if not args.growth_type:
        print("Error: REFUSE. --growth-type must be specified explicitly (MoM or YoY). Never guess.")
        sys.exit(1)
        
    try:
        # Skill 1: Load Dataset (implicitly handles null detection and reporting)
        full_data, nulls = load_dataset(args.input)
        
        # Pre-filter dataset for the specific ward and category
        filtered = [r for r in full_data if r['ward'] == args.ward and r['category'] == args.category]
        
        # Skill 2: Compute Growth (validates scoped aggregation and handles calculations)
        results = compute_growth(filtered, args.growth_type)
        
        # Ensure output directory exists
        output_dir = os.path.dirname(args.output)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            
        with open(args.output, "w", encoding="utf-8", newline="") as f:
            if not results:
                print("Warning: No matching rows found for the specified ward and category.")
                # Write empty CSV
                writer = csv.writer(f)
                writer.writerow(['period', 'actual_spend', 'growth_value', 'formula'])
            else:
                writer = csv.DictWriter(f, fieldnames=['period', 'actual_spend', 'growth_value', 'formula'])
                writer.writeheader()
                writer.writerows(results)
                
        print(f"Successfully generated growth analysis at {args.output}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
