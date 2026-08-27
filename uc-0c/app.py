"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import pandas as pd

def load_dataset(file_path):
    """
    Reads a CSV file containing ward budget data, validates the presence of required columns 
    (period, ward, category, budgeted_amount, actual_spend, notes), and reports the count of 
    null values in actual_spend along with details of which specific rows are null before 
    returning the dataset.
    
    Input: File path to the CSV file (string, e.g., '../data/budget/ward_budget.csv').
    Output: A pandas DataFrame containing the loaded data with validated columns, plus a 
    dictionary report with null count and list of null row details (including period, ward, 
    category, and notes).
    Error handling: If required columns are missing, raises a ValueError with details of 
    missing columns; if nulls are detected in actual_spend, explicitly reports them with 
    reasons from notes instead of silently handling or ignoring them, preventing silent null 
    handling failure mode.
    """
    df = pd.read_csv(file_path)
    required_cols = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
    if not all(col in df.columns for col in required_cols):
        missing = [col for col in required_cols if col not in df.columns]
        raise ValueError(f"Missing required columns: {', '.join(missing)}")
    
    null_rows = df[df['actual_spend'].isnull()]
    null_report = {
        'count': len(null_rows),
        'details': null_rows[['period', 'ward', 'category', 'notes']].to_dict('records')
    }
    
    # Explicitly report nulls to prevent silent null handling
    if null_report['count'] > 0:
        print(f"Found {null_report['count']} null values in actual_spend:")
        for detail in null_report['details']:
            print(f"  {detail['period']} · {detail['ward']} · {detail['category']} · {detail['notes']}")
    
    return df, null_report

def compute_growth(df, ward, category, growth_type):
    """
    Computes growth rates (MoM or YoY) for a specified ward and category from the loaded dataset, 
    returning a per-period table that includes actual spend, growth percentages, and the formula 
    used for each calculation.
    
    Input: Ward name (string), category name (string), growth_type (string, e.g., 'MoM' or 'YoY'), 
    and the loaded dataset (pandas DataFrame).
    Output: A pandas DataFrame with columns for period, actual_spend, growth_percentage, formula, 
    and null_flag (with reason if applicable), ensuring per-ward per-category granularity without 
    aggregation.
    Error handling: If ward or category is not found in the dataset, raises a ValueError; if 
    growth_type is invalid or not specified, refuses to proceed and prompts for clarification 
    instead of guessing; if null values are present, flags them explicitly with notes reasons 
    and skips growth computation for those rows, avoiding formula assumption and wrong aggregation 
    failure modes.
    """
    if growth_type not in ['MoM']:
        raise ValueError(f"Unsupported or unspecified growth_type '{growth_type}'. Please specify 'MoM' explicitly.")
    
    # Filter for specific ward and category to avoid aggregation across wards/categories
    filtered = df[(df['ward'] == ward) & (df['category'] == category)].copy()
    if filtered.empty:
        raise ValueError(f"No data found for ward '{ward}' and category '{category}'")
    
    # Sort by period
    filtered = filtered.sort_values('period').reset_index(drop=True)
    
    # Initialize new columns
    filtered['growth_percentage'] = None
    filtered['formula'] = ''
    filtered['null_flag'] = ''
    
    for idx in range(len(filtered)):
        row = filtered.iloc[idx]
        if pd.isnull(row['actual_spend']):
            # Flag null rows with reason from notes
            filtered.at[idx, 'null_flag'] = row['notes']
            filtered.at[idx, 'growth_percentage'] = 'NULL'
            filtered.at[idx, 'formula'] = 'Not computed due to null actual_spend'
            continue
        
        if growth_type == 'MoM':
            if idx == 0:
                # First period, no previous for MoM
                filtered.at[idx, 'growth_percentage'] = 'N/A'
                filtered.at[idx, 'formula'] = 'No previous period available for MoM calculation'
            else:
                prev_row = filtered.iloc[idx - 1]
                if pd.isnull(prev_row['actual_spend']):
                    # Previous is null, cannot compute
                    filtered.at[idx, 'growth_percentage'] = 'N/A'
                    filtered.at[idx, 'formula'] = 'Previous period actual_spend is null'
                else:
                    current = row['actual_spend']
                    previous = prev_row['actual_spend']
                    growth = ((current - previous) / previous) * 100
                    filtered.at[idx, 'growth_percentage'] = f"{growth:.1f}%"
                    filtered.at[idx, 'formula'] = f"({current} - {previous}) / {previous} * 100 = {growth:.1f}%"
    
    # Return only required columns for per-ward per-category table
    result = filtered[['period', 'actual_spend', 'growth_percentage', 'formula', 'null_flag']]
    return result

def main():
    parser = argparse.ArgumentParser(description="Compute growth rates from ward budget data.")
    parser.add_argument('--input', required=True, help="Path to input CSV file")
    parser.add_argument('--ward', required=True, help="Specific ward name")
    parser.add_argument('--category', required=True, help="Specific category name")
    parser.add_argument('--growth-type', required=True, choices=['MoM'], help="Growth type (only MoM supported)")
    parser.add_argument('--output', required=True, help="Path to output CSV file")
    
    args = parser.parse_args()
    
    # Load and validate dataset
    df, _ = load_dataset(args.input)
    
    # Compute growth for specific ward and category
    result = compute_growth(df, args.ward, args.category, args.growth_type)
    
    # Write output CSV
    result.to_csv(args.output, index=False)
    print(f"Output written to {args.output}")

if __name__ == "__main__":
    main()
