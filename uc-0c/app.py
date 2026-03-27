"""
UC-0C app.py — Budget Growth Analysis with Null Handling

Implements load_dataset and compute_growth skills following agents.md integrity rules:
- No cross-ward or cross-category aggregation
- Explicit null flagging with reasons
- Formula transparency
- Refusal on ambiguous inputs
"""
import argparse
import pandas as pd
import sys
from typing import Dict, List, Tuple, Optional


def load_dataset(file_path: str) -> Dict:
    """
    Load and validate budget CSV, report null locations before returning.
    
    Returns:
        Dict with 'dataframe' (DataFrame) and 'null_summary' (dict with count and locations)
        
    Raises:
        IOError: If file not found
        ValueError: If required columns missing
    """
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        raise IOError(f"Budget file not found: {file_path}")
    except Exception as e:
        raise IOError(f"Cannot read budget file: {e}")
    
    # Validate required columns
    required_cols = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    
    # Detect null actual_spend values
    null_rows = df[df['actual_spend'].isna()]
    null_locations = []
    
    for idx, row in null_rows.iterrows():
        null_locations.append({
            'period': row['period'],
            'ward': row['ward'],
            'category': row['category'],
            'reason': row['notes'] if pd.notna(row['notes']) else 'No reason provided'
        })
    
    null_summary = {
        'count': len(null_rows),
        'locations': null_locations
    }
    
    # Print null summary for visibility
    if null_summary['count'] > 0:
        print(f"\n⚠ WARNING: {null_summary['count']} null actual_spend values detected:\n")
        for loc in null_locations:
            print(f"  • {loc['period']} · {loc['ward']} · {loc['category']}")
            print(f"    Reason: {loc['reason']}\n")
    
    return {
        'dataframe': df,
        'null_summary': null_summary
    }


def compute_growth(data: Dict, ward: str, category: str, growth_type: str) -> pd.DataFrame:
    """
    Calculate month-over-month or year-over-year growth for ward/category.
    
    Args:
        data: Dict from load_dataset with dataframe and null_summary
        ward: Exact ward name
        category: Exact category name
        growth_type: 'MoM' or 'YoY'
        
    Returns:
        DataFrame with period, actual_spend, growth_percent, formula_used, null_flag, null_reason
        
    Raises:
        ValueError: If growth_type invalid, ward/category not found, or missing growth_type
    """
    if growth_type not in ['MoM', 'YoY']:
        raise ValueError(f"Growth type must be 'MoM' or 'YoY', got '{growth_type}'")
    
    df = data['dataframe']
    
    # Filter to exact ward and category
    filtered = df[(df['ward'] == ward) & (df['category'] == category)].copy()
    
    if filtered.empty:
        raise ValueError(f"No data found for ward '{ward}' and category '{category}'")
    
    # Sort by period to ensure chronological order
    filtered = filtered.sort_values('period').reset_index(drop=True)
    
    # Extract year and month from period
    filtered['year'] = filtered['period'].str[:4].astype(int)
    filtered['month'] = filtered['period'].str[5:7].astype(int)
    
    # Build output
    output_rows = []
    
    for idx, row in filtered.iterrows():
        current_period = row['period']
        current_spend = row['actual_spend']
        
        # Check for null
        if pd.isna(current_spend):
            output_rows.append({
                'period': current_period,
                'actual_spend': 'NULL',
                'growth_percent': 'NULL_FLAG',
                'formula_used': 'N/A (null actual_spend)',
                'null_flag': 'YES',
                'null_reason': row['notes'] if pd.notna(row['notes']) else 'No reason provided',
                'ward': ward,
                'category': category
            })
            continue
        
        # Compute growth
        growth_percent = None
        formula = None
        prev_spend = None
        
        if growth_type == 'MoM':
            # Find previous month's data
            if idx > 0:
                prev_row = filtered.iloc[idx - 1]
                if not pd.isna(prev_row['actual_spend']):
                    prev_spend = prev_row['actual_spend']
                    growth_percent = ((current_spend / prev_spend) - 1) * 100
                    formula = f"({current_spend} / {prev_spend} - 1) * 100"
        
        elif growth_type == 'YoY':
            # Find previous year's data for same month
            prev_year_data = filtered[
                (filtered['year'] == row['year'] - 1) & 
                (filtered['month'] == row['month'])
            ]
            if not prev_year_data.empty:
                prev_row = prev_year_data.iloc[0]
                if not pd.isna(prev_row['actual_spend']):
                    prev_spend = prev_row['actual_spend']
                    growth_percent = ((current_spend / prev_spend) - 1) * 100
                    formula = f"({current_spend} / {prev_spend} - 1) * 100"
        
        # Format output
        if growth_percent is not None:
            output_rows.append({
                'period': current_period,
                'actual_spend': f"{current_spend:.1f}",
                'growth_percent': f"{growth_percent:+.1f}%",
                'formula_used': formula,
                'null_flag': 'NO',
                'null_reason': '',
                'ward': ward,
                'category': category
            })
        else:
            output_rows.append({
                'period': current_period,
                'actual_spend': f"{current_spend:.1f}",
                'growth_percent': 'N/A',
                'formula_used': 'N/A (no prior period)',
                'null_flag': 'NO',
                'null_reason': '',
                'ward': ward,
                'category': category
            })
    
    return pd.DataFrame(output_rows)


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Analysis")
    parser.add_argument("--input", required=True, help="Input budget CSV file path")
    parser.add_argument("--ward", required=True, help="Ward name")
    parser.add_argument("--category", required=True, help="Category name")
    parser.add_argument("--growth-type", required=True, help="Growth type: MoM or YoY")
    parser.add_argument("--output", required=True, help="Output CSV file path")
    
    args = parser.parse_args()
    
    try:
        # Validate growth-type is specified
        if not args.growth_type:
            raise ValueError("--growth-type must be specified: use MoM or YoY")
        
        # Skill 1: Load and validate dataset
        print(f"Loading budget data from: {args.input}")
        data = load_dataset(args.input)
        
        # Skill 2: Compute growth
        print(f"\nCalculating {args.growth_type} growth for:")
        print(f"  Ward: {args.ward}")
        print(f"  Category: {args.category}")
        
        growth_df = compute_growth(data, args.ward, args.category, args.growth_type)
        
        # Write output
        growth_df.to_csv(args.output, index=False)
        
        print(f"\n✓ Growth analysis written to: {args.output}")
        print(f"✓ Total rows: {len(growth_df)}")
        print(f"✓ Formula transparency: enabled")
        print(f"\nSample output:")
        print(growth_df.head(10).to_string(index=False))
        
    except ValueError as e:
        print(f"ERROR (Validation): {e}")
        sys.exit(1)
    except IOError as e:
        print(f"ERROR (File I/O): {e}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR (Unexpected): {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
