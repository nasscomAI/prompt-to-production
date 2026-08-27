"""
UC-0C app.py — Budget Growth Calculator
Starter file. Build this using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse
import csv
import os
import sys

def load_dataset(input_path: str) -> list:
    """
    Read CSV, validate columns, report details of null rows in actual_spend.
    Returns: list of dict rows.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
        
    rows = []
    null_rows = []
    
    with open(input_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        required_cols = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
        for col in required_cols:
            if col not in reader.fieldnames:
                raise ValueError(f"Missing required column in CSV: {col}")
                
        for row in reader:
            rows.append(row)
            if not row['actual_spend'].strip():
                null_rows.append(row)
                
    # Report details of null rows
    print(f"Dataset loaded. Total rows: {len(rows)}")
    print(f"Deliberate null values detected: {len(null_rows)}")
    for nr in null_rows:
        print(f" - {nr['period']} · {nr['ward']} · {nr['category']} | Reason: {nr['notes']}")
        
    return rows


def compute_growth(dataset: list, ward: str, category: str, growth_type: str) -> list:
    """
    Takes dataset, ward, category, and growth_type, and calculates growth per period.
    Returns: list of dict rows for output.
    """
    # 1. Enforcement Rule: If --growth-type not specified — refuse and ask, never guess
    if not growth_type:
        print("ERROR: --growth-type parameter is required. Cannot guess the growth calculation formula.")
        sys.exit(1)
        
    if growth_type != "MoM":
        print(f"ERROR: Unsupported growth-type: '{growth_type}'. Only 'MoM' is supported.")
        sys.exit(1)
        
    # 2. Enforcement Rule: Never aggregate across wards or categories unless explicitly instructed
    if not ward or ward.lower() in ['any', 'all', 'aggregated', 'total', '']:
        print("ERROR: The agent is restricted from aggregating across multiple wards. A specific ward must be provided.")
        sys.exit(1)
        
    if not category or category.lower() in ['any', 'all', 'aggregated', 'total', '']:
        print("ERROR: The agent is restricted from aggregating across multiple categories. A specific category must be provided.")
        sys.exit(1)
        
    # Filter dataset by ward and category
    filtered_rows = []
    for row in dataset:
        if row['ward'].strip() == ward.strip() and row['category'].strip() == category.strip():
            filtered_rows.append(row)
            
    if not filtered_rows:
        print(f"ERROR: No data found matching ward '{ward}' and category '{category}'.")
        sys.exit(1)
        
    # Sort chronologically by period
    filtered_rows.sort(key=lambda r: r['period'])
    
    results = []
    
    for i, row in enumerate(filtered_rows):
        period = row['period']
        actual_spend_str = row['actual_spend'].strip()
        notes = row['notes'].strip()
        
        # Check if current spend is null
        if not actual_spend_str:
            results.append({
                'period': period,
                'ward': ward,
                'category': category,
                'actual_spend': 'NULL',
                'growth': 'NULL',
                'formula': 'N/A',
                'notes': f"NULL - {notes}"
            })
            continue
            
        curr_spend = float(actual_spend_str)
        
        # First period in dataset has no predecessor
        if i == 0:
            results.append({
                'period': period,
                'ward': ward,
                'category': category,
                'actual_spend': curr_spend,
                'growth': 'n/a',
                'formula': 'N/A',
                'notes': 'First period in dataset (base)'
            })
            continue
            
        # Get previous row
        prev_row = filtered_rows[i - 1]
        prev_spend_str = prev_row['actual_spend'].strip()
        
        # Check if previous spend was null
        if not prev_spend_str:
            results.append({
                'period': period,
                'ward': ward,
                'category': category,
                'actual_spend': curr_spend,
                'growth': 'NULL',
                'formula': 'N/A',
                'notes': f"NULL - Previous month's spend was NULL: {prev_row['notes'].strip()}"
            })
            continue
            
        prev_spend = float(prev_spend_str)
        
        # Compute MoM growth
        diff = (curr_spend - prev_spend) / prev_spend
        # Use proper minus sign \u2212 if negative, else '+'
        growth_str = f"+{diff*100:.1f}%" if diff >= 0 else f"\u2212{abs(diff)*100:.1f}%"
        
        formula_str = f"({curr_spend} - {prev_spend}) / {prev_spend}"
        
        results.append({
            'period': period,
            'ward': ward,
            'category': category,
            'actual_spend': curr_spend,
            'growth': growth_str,
            'formula': formula_str,
            'notes': notes if notes else 'Computed successfully'
        })
        
    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=False, help="Ward name (e.g. 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=False, help="Category name (e.g. 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", required=False, help="Growth type (e.g. 'MoM')")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Load dataset
    dataset = load_dataset(args.input)
    
    # Compute growth (will handle refusals inside)
    results = compute_growth(dataset, args.ward, args.category, args.growth_type)
    
    # Write output to CSV
    output_headers = ['period', 'ward', 'category', 'actual_spend', 'growth', 'formula', 'notes']
    with open(args.output, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=output_headers)
        writer.writeheader()
        writer.writerows(results)
        
    print(f"Growth calculation successfully written to {args.output}")


if __name__ == "__main__":
    main()
