import argparse
import os
import pandas as pd


def load_dataset(file_path: str):
    """
    Reads CSV, validates columns, reports nulls before returning.
    Returns: (df, null_report)
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Dataset not found: {file_path}")
    
    df = pd.read_csv(file_path)
    
    required_cols = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
    missing_cols = [c for c in required_cols if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing columns: {missing_cols}")
    
    # Find null actual_spend rows
    null_mask = df["actual_spend"].isna()
    null_rows = df[null_mask]
    
    null_report = []
    for _, row in null_rows.iterrows():
        null_report.append({
            "period": row["period"],
            "ward": row["ward"],
            "category": row["category"],
            "reason": row.get("notes", "No note provided")
        })
    
    print(f"Dataset loaded: {len(df)} rows")
    print(f"Null actual_spend rows found: {len(null_report)}")
    for nr in null_report:
        print(f"  - {nr['period']} | {nr['ward']} | {nr['category']} | Reason: {nr['reason']}")
    
    return df, null_report


def compute_growth(df, ward: str, category: str, growth_type: str):
    """
    Compute growth for a specific ward + category.
    Returns DataFrame with growth calculations.
    """
    # Filter
    filtered = df[(df["ward"] == ward) & (df["category"] == category)].copy()
    
    if filtered.empty:
        raise ValueError(f"No data found for ward='{ward}' and category='{category}'")
    
    # Sort by period
    filtered = filtered.sort_values("period").reset_index(drop=True)
    
    results = []
    
    for i, row in filtered.iterrows():
        period = row["period"]
        actual = row["actual_spend"]
        notes = row.get("notes", "")
        
        # Check if current is null
        if pd.isna(actual):
            results.append({
                "period": period,
                "actual_spend": "NULL",
                "prev_period": "",
                "prev_value": "",
                "growth_pct": "",
                "formula": "",
                "null_flag": f"NULL — {notes}"
            })
            continue
        
        # Compute growth based on type
        growth_pct = None
        prev_value = None
        prev_period = None
        formula = ""
        
        if growth_type.upper() == "MOM":
            # Month-over-Month: compare with previous month
            if i > 0:
                prev_row = filtered.iloc[i - 1]
                prev_value = prev_row["actual_spend"]
                prev_period = prev_row["period"]
                
                if pd.isna(prev_value):
                    growth_pct = None
                    formula = f"MoM = (({actual} - NULL) / NULL) * 100 → cannot compute (previous month is NULL)"
                else:
                    growth_pct = ((actual - prev_value) / prev_value) * 100
                    formula = f"MoM = (({actual} - {prev_value}) / {prev_value}) * 100 = {growth_pct:.2f}%"
            else:
                formula = "MoM = no previous month data (first period)"
        
        elif growth_type.upper() == "YOY":
            # Year-over-Year: compare with same month last year
            # Parse period as YYYY-MM
            try:
                year, month = int(period[:4]), int(period[5:7])
                prev_year_period = f"{year - 1}-{period[5:]}"
                prev_rows = filtered[filtered["period"] == prev_year_period]
                
                if not prev_rows.empty:
                    prev_value = prev_rows.iloc[0]["actual_spend"]
                    prev_period = prev_year_period
                    
                    if pd.isna(prev_value):
                        growth_pct = None
                        formula = f"YoY = (({actual} - NULL) / NULL) * 100 → cannot compute (previous year is NULL)"
                    else:
                        growth_pct = ((actual - prev_value) / prev_value) * 100
                        formula = f"YoY = (({actual} - {prev_value}) / {prev_value}) * 100 = {growth_pct:.2f}%"
                else:
                    formula = f"YoY = no data for {prev_year_period} (previous year not in dataset)"
            except Exception:
                formula = "YoY = period format error"
        else:
            raise ValueError(f"Unsupported growth_type: {growth_type}. Use MoM or YoY.")
        
        results.append({
            "period": period,
            "actual_spend": actual,
            "prev_period": prev_period if prev_period else "",
            "prev_value": prev_value if prev_value is not None else "",
            "growth_pct": f"{growth_pct:.2f}%" if growth_pct is not None else "N/A",
            "formula": formula,
            "null_flag": ""
        })
    
    return pd.DataFrame(results)


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Analyzer")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name to analyze")
    parser.add_argument("--category", required=True, help="Category name to analyze")
    parser.add_argument("--growth-type", required=True, help="MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()
    
    # Refuse all-ward or all-category aggregation
    if args.ward.strip().lower() in ["all", "*", ""]:
        raise ValueError("REFUSED: All-ward aggregation is not permitted. Specify a single ward.")
    if args.category.strip().lower() in ["all", "*", ""]:
        raise ValueError("REFUSED: All-category aggregation is not permitted. Specify a single category.")
    
    # Load and validate
    df, null_report = load_dataset(args.input)
    
    # Compute
    result_df = compute_growth(df, args.ward, args.category, args.growth_type)
    
    # Write output
    result_df.to_csv(args.output, index=False)
    print(f"\nDone. Growth analysis written to {args.output}")
    print(f"Rows in output: {len(result_df)}")


if __name__ == "__main__":
    main()