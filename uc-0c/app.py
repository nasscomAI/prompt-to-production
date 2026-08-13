# app.py - UC-0C Budget Growth Analyzer
import argparse
import pandas as pd


def load_dataset(input_path):
    """Load and validate the budget dataset."""
    df = pd.read_csv(input_path)
    
    # Validate required columns
    required_columns = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")
    
    # Report null actual_spend values
    null_rows = df[df["actual_spend"].isnull()]
    if not null_rows.empty:
        print(f"Warning: {len(null_rows)} rows have null actual_spend values. These will be flagged in the output.")
    
    return df


def compute_growth(df, ward, category, growth_type, output_path):
    """Compute growth metrics for a specific ward and category."""
    # Filter data for the specified ward and category
    filtered_df = df[(df["ward"] == ward) & (df["category"] == category)].copy()
    
    if filtered_df.empty:
        raise ValueError(f"No data found for ward: {ward} and category: {category}")
    
    # Sort by period
    filtered_df["period"] = pd.to_datetime(filtered_df["period"])
    filtered_df = filtered_df.sort_values("period")
    
    # Compute growth
    filtered_df["growth_pct"] = None
    filtered_df["formula"] = ""
    filtered_df["flag"] = ""
    
    for i in range(1, len(filtered_df)):
        current_spend = filtered_df.iloc[i]["actual_spend"]
        previous_spend = filtered_df.iloc[i-1]["actual_spend"]
        
        if pd.isnull(current_spend) or pd.isnull(previous_spend):
            filtered_df.at[filtered_df.index[i], "flag"] = "NULL_VALUE: Growth not computed due to null actual_spend."
            continue
        
        if growth_type == "MoM":
            growth_pct = ((current_spend - previous_spend) / previous_spend) * 100
            formula = f"(({current_spend} - {previous_spend}) / {previous_spend}) * 100"
        else:
            raise ValueError(f"Unsupported growth type: {growth_type}")
        
        filtered_df.at[filtered_df.index[i], "growth_pct"] = f"{growth_pct:.1f}%"
        filtered_df.at[filtered_df.index[i], "formula"] = formula
    
    # Flag null values
    null_mask = filtered_df["actual_spend"].isnull()
    filtered_df.loc[null_mask, "flag"] = "NULL_VALUE: Growth not computed due to null actual_spend."
    
    # Reset period to original format
    filtered_df["period"] = filtered_df["period"].dt.strftime("%Y-%m")
    
    # Save output
    output_cols = ["period", "ward", "category", "actual_spend", "growth_pct", "formula", "flag"]
    filtered_df[output_cols].to_csv(output_path, index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compute budget growth metrics.")
    parser.add_argument("--input", required=True, help="Path to input CSV file.")
    parser.add_argument("--ward", required=True, help="Ward name (e.g., 'Ward 1 – Kasba').")
    parser.add_argument("--category", required=True, help="Category name (e.g., 'Roads & Pothole Repair').")
    parser.add_argument("--growth-type", required=True, choices=["MoM"], help="Growth type (e.g., 'MoM').")
    parser.add_argument("--output", required=True, help="Path to output CSV file.")
    args = parser.parse_args()
    
    df = load_dataset(args.input)
    compute_growth(df, args.ward, args.category, args.growth_type, args.output)