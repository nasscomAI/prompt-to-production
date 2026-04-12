import argparse
import pandas as pd
import sys
import os

def load_dataset(file_path):
    """
    Skill: load_dataset
    Reads CSV, validates columns, and reports null values.
    """
    if not os.path.exists(file_path):
        print(f"CRITICAL ERROR: Dataset not found at {file_path}")
        sys.exit(1)
        
    # Use encoding='utf-8' to handle potential special characters in ward names
    df = pd.read_csv(file_path, encoding='utf-8')
    
    required_cols = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
    if not all(col in df.columns for col in required_cols):
        print(f"CRITICAL ERROR: Dataset missing required columns. Expected: {required_cols}")
        sys.exit(1)
    
    # Report null count and locations as required by skills.md
    null_rows = df[df['actual_spend'].isna()]
    print(f"--- Dataset Validation ---")
    print(f"Total rows: {len(df)}")
    print(f"Rows with null actual_spend: {len(null_rows)}")
    if not null_rows.empty:
        for _, row in null_rows.iterrows():
            print(f"  - NULL found: {row['period']} | {row['ward']} | {row['category']} | Reason: {row['notes']}")
    print(f"--------------------------\n")
            
    return df

def compute_growth(df, ward, category, growth_type):
    """
    Skill: compute_growth
    Calculates growth (MoM) for a specific ward and category.
    """
    # Enforcement: Never aggregate across wards or categories unless explicitly instructed
    # Refuse if 'all' or 'Any' passed as per README/agents.md
    if ward.lower() in ["all", "any"] or category.lower() in ["all", "any"]:
        print("CRITICAL REFUSAL: Aggregation across multiple wards or categories is strictly forbidden.")
        print("This policy prevents misleading 'total' growth numbers that mask local variations.")
        sys.exit(1)

    # Filter data to ensure per-ward, per-category output
    subset = df[(df['ward'] == ward) & (df['category'] == category)].copy()
    
    if subset.empty:
        print(f"CRITICAL ERROR: No data found for Ward: '{ward}' and Category: '{category}'.")
        print("Please verify the exact names (case-sensitive) in the dataset.")
        sys.exit(1)
        
    subset = subset.sort_values('period')
    
    results = []
    prev_spend = None
    
    for _, row in subset.iterrows():
        curr_spend = row['actual_spend']
        period = row['period']
        notes = row['notes']
        
        growth_val = ""
        formula = ""
        
        # Enforcement: Flag every null row before computing — report null reason
        if pd.isna(curr_spend):
            growth_val = "NULL"
            formula = f"REFUSE-CALC: {notes}"
        elif prev_spend is None or pd.isna(prev_spend):
            # Cannot calculate MoM if no previous month data or previous month is NULL
            growth_val = "n/a"
            formula = "Formula: Missing previous period data"
        else:
            # Standard MoM calculation
            growth = ((curr_spend - prev_spend) / prev_spend) * 100
            growth_val = f"{growth:+.1f}%"
            # Enforcement: Show formula used in every output row alongside the result
            formula = f"formula: ({curr_spend} - {prev_spend}) / {prev_spend}"
            
        results.append({
            'Ward': ward,
            'Category': category,
            'Period': period,
            'Actual Spend (₹ lakh)': curr_spend if not pd.isna(curr_spend) else "NULL",
            'MoM Growth': growth_val,
            'Formula': formula
        })
        
        prev_spend = curr_spend
        
    return pd.DataFrame(results)

def main():
    parser = argparse.ArgumentParser(description="Ward Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--ward", required=True, help="Ward name")
    parser.add_argument("--category", required=True, help="Category name")
    # Enforcement: If --growth-type not specified — refuse and ask
    parser.add_argument("--growth-type", help="Growth type (e.g., MoM)")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    
    args = parser.parse_args()
    
    # Explicit check for growth-type to comply with refusal rule
    if not args.growth_type:
        print("CRITICAL REFUSAL: --growth-type not specified.")
        print("I will not guess the calculation logic (MoM vs YoY).")
        print("Please provide --growth-type MoM to proceed.")
        sys.exit(1)
        
    if args.growth_type != "MoM":
        print(f"REFUSAL: Growth type '{args.growth_type}' is not supported. Use --growth-type MoM.")
        sys.exit(1)

    # load_dataset skill
    df = load_dataset(args.input)
    
    # compute_growth skill
    result_df = compute_growth(df, args.ward, args.category, args.growth_type)
    
    # Save output with utf-8 encoding
    result_df.to_csv(args.output, index=False, encoding='utf-8')
    print(f"SUCCESS: Results saved to {args.output}")
    print("\nOutput Preview:\n")
    try:
        print(result_df.to_string(index=False))
    except UnicodeEncodeError:
        # Fallback for environments with non-UTF8 console (like some Windows consoles)
        print(result_df.to_string(index=False).encode('ascii', 'replace').decode('ascii'))

if __name__ == "__main__":
    main()
