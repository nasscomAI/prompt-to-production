import argparse
import pandas as pd
import sys
import os

def main():
    parser = argparse.ArgumentParser(description="Civic Budget Analysis System - UC-0C")
    parser.add_argument("--input", required=True, help="Path to input CSV constraint")
    parser.add_argument("--ward", required=True, help="Exact ward name")
    parser.add_argument("--category", required=True, help="Exact category name")
    parser.add_argument("--growth-type", required=True, choices=["MoM", "YoY"], dest="growth_type")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    
    # Parse args and implicitly handle missing/invalid choices
    try:
        args = parser.parse_args()
    except SystemExit:
        sys.exit(1) # argparse will already print the error message

    # Input validation for ambiguous terms
    ambiguous_terms = ["overall", "all", "combined", "any"]
    if args.ward.lower() in ambiguous_terms or args.category.lower() in ambiguous_terms:
        print("Error: Ambiguous inputs like 'overall' or 'all' are not allowed.", file=sys.stderr)
        sys.exit(1)

    # Check if input file exists
    if not os.path.exists(args.input):
        print(f"Error: Input file not found at {args.input}", file=sys.stderr)
        sys.exit(1)

    # Load dataset
    try:
        df = pd.read_csv(args.input)
    except Exception as e:
        print(f"Error reading CSV: {e}", file=sys.stderr)
        sys.exit(1)

    # Validate required columns
    required_cols = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        print(f"Error: Missing required columns: {', '.join(missing_cols)}", file=sys.stderr)
        sys.exit(1)

    # Filter data specific to ward and category
    filtered_df = df[(df["ward"] == args.ward) & (df["category"] == args.category)].copy()

    if filtered_df.empty:
        print("Error: No data found for the specified ward and category.", file=sys.stderr)
        sys.exit(1)

    # Aggregation rule check
    if filtered_df["ward"].nunique() > 1 or filtered_df["category"].nunique() > 1:
        print("Error: Multiple wards or categories detected. Aggregation is strictly prohibited.", file=sys.stderr)
        sys.exit(1)

    # Parse period to explicitly handle time
    try:
        filtered_df["period_dt"] = pd.to_datetime(filtered_df["period"], format="%Y-%m")
    except Exception as e:
        print("Error: Invalid period format. Must be YYYY-MM.", file=sys.stderr)
        sys.exit(1)

    filtered_df = filtered_df.sort_values(by="period_dt").reset_index(drop=True)

    results = []
    
    for idx, row in filtered_df.iterrows():
        period_dt = row["period_dt"]
        period = row["period"]
        ward = row["ward"]
        category = row["category"]
        current_spend = row["actual_spend"]
        notes = str(row["notes"]).strip() if pd.notna(row["notes"]) else ""
        
        if args.growth_type == "MoM":
            target_dt = period_dt - pd.DateOffset(months=1)
            formula_str = "(current - previous) / previous * 100"
        else:
            target_dt = period_dt - pd.DateOffset(years=1)
            formula_str = "(current - same_month_last_year) / same_month_last_year * 100"
            
        # Locate previous data point
        prev_row = filtered_df[filtered_df["period_dt"] == target_dt]
        if prev_row.empty:
            prev_spend = None
        else:
            prev_spend = prev_row.iloc[0]["actual_spend"]

        null_flag = False
        growth_percentage = None
        null_reason = None
        
        # Strictly handle null values in current and previous spend
        if pd.isna(current_spend):
            null_flag = True
            current_spend = None
            null_reason = notes if notes else "Missing current spend"
            
        if pd.isna(prev_spend):
            null_flag = True
            prev_spend = None
            prev_msg = "Missing previous spend"
            if null_reason:
                if prev_msg not in null_reason:
                    null_reason += f" | {prev_msg}"
            else:
                null_reason = prev_msg
            
        # Compute growth only if both values are valid
        if not null_flag:
            if prev_spend == 0:
                null_flag = True
                null_reason = notes if notes else "Division by zero"
            else:
                growth_percentage = ((current_spend - prev_spend) / prev_spend) * 100

        results.append({
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": current_spend,
            "previous_spend": prev_spend,
            "growth_percentage": growth_percentage,
            "formula_used": formula_str,
            "null_flag": null_flag,
            "null_reason": null_reason if null_flag else None
        })

    out_df = pd.DataFrame(results)
    
    # Structure output
    output_columns = [
        "period", "ward", "category", "actual_spend", "previous_spend", 
        "growth_percentage", "formula_used", "null_flag", "null_reason"
    ]
    
    try:
        out_df[output_columns].to_csv(args.output, index=False)
        print(f"Success: Final output written to {args.output}")
    except Exception as e:
        print(f"Error writing to output file: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
