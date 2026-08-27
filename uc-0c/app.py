import argparse
import pandas as pd
import sys

def load_dataset(filepath):
    try:
        df = pd.read_csv(filepath)
    except Exception as e:
        print(f"Error loading file: {e}")
        sys.exit(1)
        
    expected_cols = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
    if not expected_cols.issubset(df.columns):
        print(f"Error: Dataset is missing expected columns. Found: {df.columns}")
        sys.exit(1)

    null_rows = df[df['actual_spend'].isnull()]
    null_count = len(null_rows)
    
    if null_count > 0:
        print(f"Dataset loaded. Found {null_count} rows with null actual_spend.")
        print("Detailed null rows:")
        for _, row in null_rows.iterrows():
            reason = row['notes'] if pd.notna(row['notes']) else "No reason provided"
            print(f" - {row['period']} | {row['ward']} | {row['category']} | Reason: {reason}")
    else:
        print("Dataset loaded successfully. No null actual_spend records found.")
        
    return df

def compute_growth(df, ward, category, growth_type):
    if not growth_type:
        print("Error: Growth type not specified. System refuses to guess. Please provide --growth-type.")
        sys.exit(1)
        
    if not ward or ward.lower() == 'all' or not category or category.lower() == 'all':
        print("Error: Aggregating across all wards or categories is strictly forbidden unless explicitly instructed. Refusing to compute.")
        sys.exit(1)

    # Filter data
    subset = df[(df['ward'] == ward) & (df['category'] == category)].copy()
    
    if subset.empty:
        print(f"No data found for Ward: '{ward}' and Category: '{category}'.")
        sys.exit(1)

    subset = subset.sort_values(by='period').reset_index(drop=True)
    
    results = []
    
    for i in range(len(subset)):
        curr_row = subset.iloc[i]
        curr_val = curr_row['actual_spend']
        note = curr_row['notes']
        
        # Determine previous value based on growth type
        prev_val = None
        prev_period = None
        if growth_type.lower() == 'mom':
            if i > 0:
                prev_val = subset.iloc[i-1]['actual_spend']
                prev_period = subset.iloc[i-1]['period']
        elif growth_type.lower() == 'yoy':
            if i >= 12:
                prev_val = subset.iloc[i-12]['actual_spend']
                prev_period = subset.iloc[i-12]['period']
        else:
            print(f"Error: Unsupported growth type '{growth_type}'. Use 'MoM' or 'YoY'.")
            sys.exit(1)
            
        # Calculation logic matching enforcement rules
        if pd.isna(curr_val):
            growth = "NULL"
            reason = note if pd.notna(note) else "No reason provided"
            formula = f"Must be flagged — not computed (Reason: {reason})"
        elif prev_val is not None and pd.isna(prev_val):
            # Previous value is null
            growth = "N/A"
            formula = f"Cannot compute: previous period ({prev_period}) has null actual spend."
        elif i == 0 and growth_type.lower() == 'mom':
            growth = "N/A"
            formula = "First period - no previous data for MoM"
        elif i < 12 and growth_type.lower() == 'yoy':
            growth = "N/A"
            formula = "First year - no previous data for YoY"
        elif prev_val == 0:
            growth = "N/A"
            formula = "Cannot divide by zero (previous spend was 0)"
        else:
            pct = ((curr_val - prev_val) / prev_val) * 100
            sign = "+" if pct > 0 else ""
            growth = f"{sign}{pct:.1f}%"
            formula = f"({curr_val} - {prev_val}) / {prev_val} * 100"
            if pd.notna(note) and str(note).strip():
                growth += f" ({note})"
                
        results.append({
            'Ward': curr_row['ward'],
            'Category': curr_row['category'],
            'Period': curr_row['period'],
            'Actual Spend': "NULL" if pd.isna(curr_val) else curr_val,
            f'{growth_type.upper()} Growth': growth,
            'Formula Used': formula
        })
        
    return pd.DataFrame(results)

def main():
    parser = argparse.ArgumentParser(description="Financial Data Analyst Agent - Budget Growth Metrics")
    parser.add_argument('--input', required=True, help="Path to input CSV dataset")
    parser.add_argument('--ward', help="Specific ward to analyze (refuses 'All')")
    parser.add_argument('--category', help="Specific category to analyze (refuses 'All')")
    parser.add_argument('--growth-type', help="Type of growth to compute (e.g., 'MoM', 'YoY')")
    parser.add_argument('--output', required=True, help="Path to save output CSV")
    
    args = parser.parse_args()
    
    # Check for missing arguments proactively
    if not args.ward or not args.category:
        print("Error: --ward and --category must be explicitly specified. Aggregation without instruction is refused.")
        sys.exit(1)
        
    if not args.growth_type:
        print("Error: --growth-type not specified. System refuses and asks, never guesses. Please provide it.")
        sys.exit(1)

    df = load_dataset(args.input)
    
    result_df = compute_growth(df, args.ward, args.category, args.growth_type)
    
    result_df.to_csv(args.output, index=False)
    print(f"Successfully computed requested metrics and saved to '{args.output}'.")

if __name__ == "__main__":
    main()
