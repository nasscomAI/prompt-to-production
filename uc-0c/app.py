"""
UC-0C app.py — Municipal budget growth calculation with strict validation and null-flagging.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse
import csv
import sys
import os
import re

def normalize_name(name: str) -> str:
    """
    Normalizes ward or category names for robust matching.
    Replaces en-dash, em-dash, and standardizes spacing and case.
    """
    if not name:
        return ""
    name = name.replace('\u2013', '-').replace('\u2014', '-')
    name = re.sub(r'\s+', ' ', name)
    return name.strip().lower()

def load_dataset(input_path: str) -> list:
    """
    Reads CSV, validates columns, reports null count and which rows before returning.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input budget file not found: {input_path}")
        
    required_cols = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
    rows = []
    
    with open(input_path, 'r', encoding='utf-8', errors='replace') as f:
        reader = csv.DictReader(f)
        # Validate columns
        for col in required_cols:
            if col not in reader.fieldnames:
                raise ValueError(f"Missing required column in budget dataset: {col}")
                
        null_count = 0
        null_details = []
        
        for idx, row in enumerate(reader):
            # Check for null actual_spend
            actual_spend = row['actual_spend'].strip()
            if not actual_spend:
                null_count += 1
                line_num = idx + 2  # 1-indexed plus header row
                null_details.append(
                    f"Line {line_num}: period={row['period']}, ward={row['ward']}, category={row['category']}, notes='{row['notes']}'"
                )
            rows.append(row)
            
    print(f"Dataset successfully loaded. Total rows: {len(rows)}")
    print(f"Found {null_count} null actual_spend rows:")
    for detail in null_details:
        print(f"  {detail}")
        
    return rows

def compute_growth(ward: str, category: str, growth_type: str, dataset: list) -> list:
    """
    Takes ward + category + growth_type, returns per-period table with formula shown.
    Refuses cross-ward or cross-category aggregations.
    """
    norm_ward = normalize_name(ward)
    norm_cat = normalize_name(category)
    
    # Filter dataset for specific ward and category
    filtered = []
    for r in dataset:
        if normalize_name(r['ward']) == norm_ward and normalize_name(r['category']) == norm_cat:
            filtered.append(r)
            
    if not filtered:
        print(f"Warning: No rows matched ward='{ward}' and category='{category}'", file=sys.stderr)
        
    # Sort by period chronologically
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    for idx, row in enumerate(filtered):
        period = row['period']
        actual_str = row['actual_spend'].strip()
        
        # Check if current actual_spend is null
        if not actual_str:
            results.append({
                'period': period,
                'ward': row['ward'],
                'category': row['category'],
                'budgeted_amount': row['budgeted_amount'],
                'actual_spend': 'NULL',
                'growth': 'NULL',
                'formula': f"NULL (Reason: {row['notes']})"
            })
            continue
            
        current_actual = float(actual_str)
        
        # Calculate growth based on growth_type (MoM supported)
        if growth_type.lower() == 'mom':
            if idx == 0:
                results.append({
                    'period': period,
                    'ward': row['ward'],
                    'category': row['category'],
                    'budgeted_amount': row['budgeted_amount'],
                    'actual_spend': actual_str,
                    'growth': 'n/a',
                    'formula': 'n/a (First period, no baseline)'
                })
            else:
                prev_row = filtered[idx - 1]
                prev_actual_str = prev_row['actual_spend'].strip()
                
                # Check if previous period actual_spend was null
                if not prev_actual_str:
                    results.append({
                        'period': period,
                        'ward': row['ward'],
                        'category': row['category'],
                        'budgeted_amount': row['budgeted_amount'],
                        'actual_spend': actual_str,
                        'growth': 'n/a',
                        'formula': f"n/a (Previous period {prev_row['period']} actual spend was NULL)"
                    })
                else:
                    prev_actual = float(prev_actual_str)
                    if prev_actual == 0:
                        results.append({
                            'period': period,
                            'ward': row['ward'],
                            'category': row['category'],
                            'budgeted_amount': row['budgeted_amount'],
                            'actual_spend': actual_str,
                            'growth': 'n/a',
                            'formula': 'n/a (Previous period actual spend was 0)'
                        })
                    else:
                        growth_val = ((current_actual - prev_actual) / prev_actual) * 100
                        # Format growth with correct sign representation
                        if growth_val > 0:
                            growth_str = f"+{growth_val:.1f}%"
                        elif growth_val < 0:
                            # Using Unicode minus sign U+2212
                            growth_str = f"\u2212{abs(growth_val):.1f}%"
                        else:
                            growth_str = "0.0%"
                            
                        formula_str = f"({current_actual:.1f} - {prev_actual:.1f}) / {prev_actual:.1f}"
                        results.append({
                            'period': period,
                            'ward': row['ward'],
                            'category': row['category'],
                            'budgeted_amount': row['budgeted_amount'],
                            'actual_spend': actual_str,
                            'growth': growth_str,
                            'formula': formula_str
                        })
        else:
            raise NotImplementedError(f"Growth type '{growth_type}' is not supported yet.")
            
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to input CSV file")
    parser.add_argument("--ward", help="Name of the ward (refuses 'any' or 'all')")
    parser.add_argument("--category", help="Name of the budget category (refuses 'any' or 'all')")
    parser.add_argument("--growth-type", help="Type of growth computation (MoM, YoY) (never guess)")
    parser.add_argument("--output", required=True, help="Path to output CSV file")
    args = parser.parse_args()
    
    # 1. Growth-type must be specified - refuse and ask, never guess
    if not args.growth_type:
        print("Refusal: Growth type is not specified. Please specify --growth-type (e.g. MoM).", file=sys.stderr)
        sys.exit(1)
        
    # 2. Never aggregate across wards or categories - refuse if asked
    if not args.ward or args.ward.lower() in ['any', 'all', 'all-ward', 'all-wards', 'all wards']:
        print("Refusal: Ward must be specified and cannot be 'any' or 'all'. All-ward aggregation is not permitted.", file=sys.stderr)
        sys.exit(1)
        
    if not args.category or args.category.lower() in ['any', 'all', 'all-category', 'all-categories', 'all categories']:
        print("Refusal: Category must be specified and cannot be 'any' or 'all'. All-category aggregation is not permitted.", file=sys.stderr)
        sys.exit(1)
        
    try:
        # Load dataset (validates and reports null rows)
        dataset = load_dataset(args.input)
        
        # Compute growth (safe null handling, includes formulas)
        results = compute_growth(args.ward, args.category, args.growth_type, dataset)
        
        # Write output to CSV
        out_dir = os.path.dirname(args.output)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
            
        with open(args.output, 'w', encoding='utf-8', newline='') as f:
            fieldnames = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'growth', 'formula']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in results:
                writer.writerow(r)
                
        print(f"Growth calculation written to {args.output}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
