import argparse
import pandas as pd
import sys

def run_analysis(input_path, ward, category, growth_type, output_path):
    # 1. Validation Logic (Enforcement)
    if not growth_type:
        print("❌ Error: Growth type not specified. Please choose MoM.")
        sys.exit(1)
    
    df = pd.read_csv(input_path, encoding='utf-8')
    
    # 2. Filter data for isolation
    mask = (df['ward'] == ward) & (df['category'] == category)
    filtered_df = df[mask].copy()
    
    if filtered_df.empty:
        print(f"❌ Error: No data found for Ward: {ward} and Category: {category}")
        return

    # 3. Handle MoM Growth
    filtered_df['actual_spend'] = pd.to_numeric(filtered_df['actual_spend'], errors='coerce')
    filtered_df['prev_spend'] = filtered_df['actual_spend'].shift(1)
    
    # Formula: (Current - Previous) / Previous * 100
    filtered_df['growth_pct'] = ((filtered_df['actual_spend'] - filtered_df['prev_spend']) / filtered_df['prev_spend']) * 100
    filtered_df['formula'] = "((Actual - Previous) / Previous) * 100"
    
    # 4. Null Reporting (from notes)
    filtered_df['status'] = filtered_df.apply(
        lambda row: f"NULL: {row['notes']}" if pd.isna(row['actual_spend']) else "OK", axis=1
    )

    filtered_df.to_csv(output_path, index=False)
    print(f"✅ Growth analysis for {ward} saved to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type") # We check if this is missing
    parser.add_argument("--output", required=True)
    
    args = parser.parse_args()
    run_analysis(args.input, args.ward, args.category, args.growth_type, args.output)