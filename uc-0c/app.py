"""
UC-0C app.py — Number That Looks Right
Calculates Month-over-Month growth for specific ward and category
"""
import argparse
import pandas as pd
import numpy as np
import sys

def load_dataset(file_path):
    """
    Reads the ward budget CSV and reports null actual_spend values
    """
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found")
        sys.exit(1)
    
    # Validate required columns
    required = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
    missing = [col for col in required if col not in df.columns]
    if missing:
        print(f"Error: Missing required columns: {missing}")
        sys.exit(1)
    
    # Report null values
    null_rows = df[df['actual_spend'].isna()]
    print(f"\n📊 Dataset loaded: {len(df)} rows")
    print(f"⚠️  Found {len(null_rows)} rows with null actual_spend:")
    
    for idx, row in null_rows.iterrows():
        print(f"   - {row['period']} | {row['ward']} | {row['category']} | Reason: {row['notes']}")
    
    return df

def compute_growth(data, ward, category, growth_type):
    """
    Calculates Month-over-Month growth for specific ward and category
    """
    if growth_type != "MoM":
        raise ValueError(f"Growth type '{growth_type}' not supported. Please specify 'MoM' (Month-over-Month)")
    
    # Filter data
    filtered = data[(data['ward'] == ward) & (data['category'] == category)].copy()
    
    if len(filtered) == 0:
        available_wards = data['ward'].unique().tolist()
        available_cats = data['category'].unique().tolist()
        print(f"\n❌ No data found for Ward: '{ward}' and Category: '{category}'")
        print(f"Available wards: {available_wards}")
        print(f"Available categories: {available_cats}")
        sys.exit(1)
    
    # Sort by period
    filtered = filtered.sort_values('period')
    
    # Initialize result columns
    filtered['growth_percentage'] = np.nan
    filtered['formula_used'] = ''
    filtered['null_flag'] = filtered['actual_spend'].isna()
    filtered['null_reason'] = ''
    
    # Calculate MoM growth
    for i in range(1, len(filtered)):
        prev_spend = filtered.iloc[i-1]['actual_spend']
        curr_spend = filtered.iloc[i]['actual_spend']
        
        # Skip if either value is null
        if pd.isna(prev_spend) or pd.isna(curr_spend):
            continue
        
        # Calculate growth
        if prev_spend != 0:
            growth = ((curr_spend - prev_spend) / prev_spend) * 100
            filtered.iloc[i, filtered.columns.get_loc('growth_percentage')] = round(growth, 1)
            filtered.iloc[i, filtered.columns.get_loc('formula_used')] = "((current - previous) / previous) * 100"
    
    # Add null reasons
    for idx, row in filtered.iterrows():
        if pd.isna(row['actual_spend']):
            filtered.loc[idx, 'null_reason'] = row['notes']
    
    return filtered[['period', 'actual_spend', 'growth_percentage', 'formula_used', 'null_flag', 'null_reason']]

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward to analyze (e.g., 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=True, help="Category to analyze (e.g., 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", required=True, help="Growth type (only 'MoM' supported)")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    
    args = parser.parse_args()
    
    # Step 1: Load data
    print(f"\n🔍 Analyzing: {args.ward} | {args.category}")
    df = load_dataset(args.input)
    
    # Step 2: Compute growth
    try:
        result = compute_growth(df, args.ward, args.category, args.growth_type)
    except ValueError as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    
    # Step 3: Save results
    result.to_csv(args.output, index=False)
    print(f"\n✅ Growth calculation complete")
    print(f"📈 Results saved to: {args.output}")
    
    # Step 4: Show sample
    print("\n📋 First 5 rows of output:")
    print(result.head().to_string())

if __name__ == "__main__":
    main()