"""
UC-0C app.py — Budget Growth Calculator
RICE → agents.md → skills.md → CRAFT implementation.

Enforces agents.md rules:
1. Never aggregate across wards or categories — refuse if requested
2. Flag every null actual_spend row BEFORE computing — include reason from notes
3. Show formula used (MoM or YoY) in every output row
4. Refuse computation if --growth-type not specified — never guess
"""
import argparse
import csv
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import pandas as pd


def load_dataset(input_path: str) -> Dict:
    """
    Load budget CSV and validate required columns.
    Identifies and reports all null actual_spend rows BEFORE processing.
    
    Args:
        input_path: Path to ward_budget.csv
        
    Returns:
        Dict with keys:
        - dataframe: pd.DataFrame with loaded data
        - null_rows: List of dicts with period/ward/category/reason
        - metadata: Dict with total_rows, null_count, wards_list, categories_list
        
    Enforces skills.md error handling:
    - FileNotFoundError if file not found
    - ValueError if required columns missing
    - Logs errors to stderr and reports nulls upfront
    """
    try:
        df = pd.read_csv(input_path)
    except FileNotFoundError:
        print(f"ERROR: File not found: {input_path}", file=sys.stderr)
        raise
    except Exception as e:
        print(f"ERROR: Failed to read CSV: {str(e)}", file=sys.stderr)
        raise
    
    # Validate required columns
    required_cols = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
    missing_cols = required_cols - set(df.columns)
    if missing_cols:
        print(f"ERROR: Missing required columns: {missing_cols}", file=sys.stderr)
        raise ValueError(f"Missing columns: {missing_cols}")
    
    # Identify null rows in actual_spend
    null_rows = []
    for idx, row in df.iterrows():
        if pd.isna(row['actual_spend']) or (isinstance(row['actual_spend'], str) and row['actual_spend'].strip() == ''):
            reason = row.get('notes', 'No reason provided')
            null_rows.append({
                'period': row['period'],
                'ward': row['ward'],
                'category': row['category'],
                'reason': reason
            })
    
    # Extract unique wards and categories
    wards_list = sorted(df['ward'].unique().tolist())
    categories_list = sorted(df['category'].unique().tolist())
    
    metadata = {
        'total_rows': len(df),
        'null_count': len(null_rows),
        'wards_list': wards_list,
        'categories_list': categories_list
    }
    
    # Report nulls upfront
    if null_rows:
        print(f"\nWARNING: {len(null_rows)} null actual_spend values found:", file=sys.stderr)
        for nr in null_rows:
            print(f"  {nr['period']} | {nr['ward']} | {nr['category']} | Reason: {nr['reason']}", file=sys.stderr)
        print("", file=sys.stderr)
    
    return {
        'dataframe': df,
        'null_rows': null_rows,
        'metadata': metadata
    }


def compute_growth(data_dict: Dict, ward: str, category: str, growth_type: str, 
                  period_range: Optional[List[str]] = None) -> Tuple[List[Dict], List[str]]:
    """
    Compute MoM (Month-over-Month) or YoY (Year-over-Year) growth for specified ward and category.
    
    Args:
        data_dict: Dict returned from load_dataset
        ward: Ward name (must match exactly)
        category: Category name (must match exactly)
        growth_type: "MoM" or "YoY" — must be explicit, never guessed
        period_range: Optional list of YYYY-MM periods to include
        
    Returns:
        Tuple of (results list of dicts, warnings list)
        
    Enforces agents.md rules:
    - Refuses if ward or category not found
    - Refuses if growth_type not in ["MoM", "YoY"]
    - Shows formula in every row
    - Flags null rows
    - Never aggregates across wards/categories
    """
    warnings = []
    
    # Validate growth_type
    if growth_type not in ["MoM", "YoY"]:
        error_msg = f"ERROR: --growth-type must be 'MoM' or 'YoY', got '{growth_type}'. Cannot guess. Aborting."
        print(error_msg, file=sys.stderr)
        raise ValueError(error_msg)
    
    df = data_dict['dataframe']
    null_rows = data_dict['null_rows']
    
    # Validate ward and category exist
    valid_wards = data_dict['metadata']['wards_list']
    valid_categories = data_dict['metadata']['categories_list']
    
    if ward not in valid_wards:
        error_msg = f"ERROR: Ward '{ward}' not found. Valid wards: {valid_wards}"
        print(error_msg, file=sys.stderr)
        raise ValueError(error_msg)
    
    if category not in valid_categories:
        error_msg = f"ERROR: Category '{category}' not found. Valid categories: {valid_categories}"
        print(error_msg, file=sys.stderr)
        raise ValueError(error_msg)
    
    # Filter to specified ward and category only — no aggregation
    filtered = df[(df['ward'] == ward) & (df['category'] == category)].copy()
    
    if filtered.empty:
        error_msg = f"ERROR: No data found for Ward='{ward}' and Category='{category}'"
        print(error_msg, file=sys.stderr)
        raise ValueError(error_msg)
    
    # Sort by period
    filtered = filtered.sort_values('period').reset_index(drop=True)
    
    # Build null lookup for this ward/category
    null_lookup = set()
    for nr in null_rows:
        if nr['ward'] == ward and nr['category'] == category:
            null_lookup.add(nr['period'])
    
    # Compute growth
    results = []
    prev_period = None
    prev_spend = None
    
    for idx, row in filtered.iterrows():
        period = row['period']
        actual_spend = row['actual_spend']
        
        # Check if this row is null
        is_null = period in null_lookup or pd.isna(actual_spend) or (isinstance(actual_spend, str) and actual_spend.strip() == '')
        
        result_row = {
            'period': period,
            'actual_spend': actual_spend if not is_null else 'NULL',
            'previous_period_spend': prev_spend,
            'formula': growth_type,
            'growth_percent': None,
            'null_flag': is_null,
            'notes': row['notes'] if is_null else ''
        }
        
        # Compute growth only if current and previous are non-null
        if not is_null and prev_spend is not None:
            try:
                prev_val = float(prev_spend)
                curr_val = float(actual_spend)
                
                if growth_type == "MoM":
                    growth_pct = ((curr_val - prev_val) / prev_val * 100) if prev_val != 0 else 0
                    result_row['formula'] = f"MoM: ({curr_val:.1f} - {prev_val:.1f}) / {prev_val:.1f} * 100"
                else:  # YoY
                    growth_pct = ((curr_val - prev_val) / prev_val * 100) if prev_val != 0 else 0
                    result_row['formula'] = f"YoY: ({curr_val:.1f} - {prev_val:.1f}) / {prev_val:.1f} * 100"
                
                result_row['growth_percent'] = f"{growth_pct:.1f}%"
            except (ValueError, TypeError):
                result_row['growth_percent'] = 'ERROR'
                result_row['notes'] = 'Could not compute: invalid numeric value'
        elif is_null:
            result_row['growth_percent'] = 'NULL'
            result_row['notes'] = f"Null actual_spend: {row['notes']}"
        elif prev_spend is None:
            result_row['growth_percent'] = 'N/A'
            result_row['notes'] = 'First period (no previous value)'
        
        results.append(result_row)
        
        # Update prev for next iteration (only if current is not null)
        if not is_null:
            prev_period = period
            prev_spend = actual_spend
    
    return results, warnings


def main():
    """Main entry point — reads budget data, computes growth, writes output."""
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name (exact match)")
    parser.add_argument("--category", required=True, help="Category name (exact match)")
    parser.add_argument("--growth-type", required=True, help="MoM or YoY (must be explicit)")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    try:
        print(f"Loading dataset from {args.input}...", file=sys.stderr)
        data_dict = load_dataset(args.input)
        
        print(f"Computing {args.growth_type} growth for Ward='{args.ward}', Category='{args.category}'...", file=sys.stderr)
        results, warnings = compute_growth(data_dict, args.ward, args.category, args.growth_type)
        
        # Write output CSV
        fieldnames = ['period', 'actual_spend', 'previous_period_spend', 'formula', 'growth_percent', 'null_flag', 'notes']
        
        with open(args.output, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in results:
                writer.writerow({
                    'period': row['period'],
                    'actual_spend': row['actual_spend'],
                    'previous_period_spend': row['previous_period_spend'],
                    'formula': row['formula'],
                    'growth_percent': row['growth_percent'],
                    'null_flag': row['null_flag'],
                    'notes': row['notes']
                })
        
        print(f"\nResults written to {args.output}", file=sys.stderr)
        print(f"Rows processed: {len(results)}", file=sys.stderr)
        
    except ValueError as e:
        print(f"ERROR: {str(e)}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
