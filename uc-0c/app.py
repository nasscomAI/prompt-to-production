"""
UC-0C app.py — Budget Growth Calculation Agent Implementation.
Implements agents.md (Budget Growth Agent) and skills.md (load_dataset, compute_growth).
See README.md for run command and expected behaviour.
"""
import argparse
import pandas as pd
from pathlib import Path


def load_dataset(file_path):
    """
    Skill: load_dataset
    Reads budget CSV, validates column structure, and reports null values with reasons.
    
    Args:
        file_path (str): Path to budget CSV file
    
    Returns:
        dict: {
            "data": dataframe,
            "null_rows": list of {period, ward, category, reason},
            "summary": {total_rows, null_count}
        }
    
    Raises:
        FileNotFoundError: If file not found
        ValueError: If required columns missing or no data rows
    """
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"Dataset file not found: {file_path}")
    
    # Validate required columns
    required_cols = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
    missing_cols = required_cols - set(df.columns)
    if missing_cols:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing_cols))}")
    
    if len(df) == 0:
        raise ValueError("No data rows found in dataset")
    
    # Detect null rows (actual_spend is blank/NaN)
    null_rows = []
    for idx, row in df.iterrows():
        if pd.isna(row['actual_spend']) or (isinstance(row['actual_spend'], str) and row['actual_spend'].strip() == ''):
            null_rows.append({
                'period': row['period'],
                'ward': row['ward'],
                'category': row['category'],
                'reason': row.get('notes', 'No reason provided')
            })
    
    return {
        "data": df,
        "null_rows": null_rows,
        "summary": {
            "total_rows": len(df),
            "null_count": len(null_rows)
        }
    }


def compute_growth(dataset_info, ward, category, growth_type):
    """
    Skill: compute_growth
    Calculates per-period growth metric (MoM or YoY) for specified ward + category.
    
    Args:
        dataset_info (dict): Output from load_dataset
        ward (str): Specific ward name
        category (str): Specific category name
        growth_type (str): "MoM" or "YoY"
    
    Returns:
        DataFrame with columns=[period, actual_spend, formula_used, growth_percent, null_flagged]
    
    Raises:
        ValueError: If ward/category not found or invalid growth_type
    """
    if growth_type not in ["MoM", "YoY"]:
        raise ValueError(f"Invalid growth_type '{growth_type}'. Must be 'MoM' or 'YoY'")
    
    df = dataset_info["data"].copy()
    
    # Filter to specific ward + category
    filtered = df[(df['ward'] == ward) & (df['category'] == category)].copy()
    
    if len(filtered) == 0:
        raise ValueError(f"No data found for ward='{ward}' and category='{category}'")
    
    # Sort by period
    filtered = filtered.sort_values('period').reset_index(drop=True)
    
    # Build output table with formulas
    results = []
    for idx, row in filtered.iterrows():
        period = row['period']
        actual_spend = row['actual_spend']
        
        # Check if this is a null row
        is_null = pd.isna(actual_spend) or (isinstance(actual_spend, str) and actual_spend.strip() == '')
        
        if is_null:
            results.append({
                'period': period,
                'actual_spend': None,
                'formula_used': 'N/A',
                'growth_percent': None,
                'null_flagged': True,
                'null_reason': row.get('notes', 'No reason provided')
            })
        else:
            actual_spend = float(actual_spend)
            
            if growth_type == "MoM":
                if idx == 0:
                    # First period — no previous month
                    formula = "N/A (first period)"
                    growth = None
                else:
                    prev_spend = float(filtered.iloc[idx-1]['actual_spend'])
                    if pd.isna(prev_spend):
                        formula = "N/A (previous month is null)"
                        growth = None
                    else:
                        growth = ((actual_spend - prev_spend) / prev_spend) * 100
                        formula = f"({actual_spend}-{prev_spend})/{prev_spend}"
            else:  # YoY
                # YoY would look at previous year same period (not applicable for 12-month data)
                # For this implementation, we'll flag it as unavailable
                formula = "N/A (YoY requires multi-year data)"
                growth = None
            
            results.append({
                'period': period,
                'actual_spend': actual_spend,
                'formula_used': formula,
                'growth_percent': growth if growth is None else f"{growth:.1f}%",
                'null_flagged': False,
                'null_reason': None
            })
    
    return pd.DataFrame(results)


def main():
    parser = argparse.ArgumentParser(
        description="UC-0C: Budget Growth Calculation Agent. Computes per-ward, per-category growth metrics."
    )
    parser.add_argument('--input', required=True, help='Path to budget CSV file')
    parser.add_argument('--ward', required=True, help='Specific ward name (e.g., "Ward 1 – Kasba")')
    parser.add_argument('--category', required=True, help='Specific category (e.g., "Roads & Pothole Repair")')
    parser.add_argument('--growth-type', required=True, help='Growth type: "MoM" (Month-over-Month) or "YoY" (Year-over-Year)')
    parser.add_argument('--output', required=True, help='Path to output CSV file')
    
    args = parser.parse_args()
    
    try:
        # Enforcement: Refuse if growth-type not specified
        if not args.growth_type or args.growth_type not in ["MoM", "YoY"]:
            raise ValueError(f"--growth-type is required and must be 'MoM' or 'YoY'. Got: {args.growth_type}")
        
        # Skill 1: Load dataset with null detection
        dataset_info = load_dataset(args.input)
        
        print(f"✓ Dataset loaded: {dataset_info['summary']['total_rows']} rows")
        if dataset_info['summary']['null_count'] > 0:
            print(f"⚠ Found {dataset_info['summary']['null_count']} null rows:")
            for null_row in dataset_info['null_rows']:
                print(f"  - {null_row['period']} | {null_row['ward']} | {null_row['category']} | Reason: {null_row['reason']}")
        
        # Skill 2: Compute growth for specified ward + category
        growth_table = compute_growth(dataset_info, args.ward, args.category, args.growth_type)
        
        # Write output
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        growth_table.to_csv(args.output, index=False)
        
        print(f"✓ Growth calculation complete")
        print(f"✓ Output written to: {args.output}")
        print(f"\nGrowth Table Preview:")
        print(growth_table.to_string(index=False))
    
    except (FileNotFoundError, ValueError) as e:
        print(f"✗ Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
