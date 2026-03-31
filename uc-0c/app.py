"""
UC-0C app.py — Ward-level budget growth analysis.
Implements agents.md (UC-0C agent) + skills.md (load_dataset, compute_growth) with CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import sys
import pandas as pd
from pathlib import Path

# ============================================================================
# SKILL: load_dataset
# ============================================================================
def load_dataset(input_file):
    """
    Read CSV file, validate schema, count and list null rows before returning full dataset.
    
    Returns:
        DataFrame: Full dataset (no rows dropped), with null rows identified
    Raises:
        ValueError: If columns missing or file not found
    """
    try:
        df = pd.read_csv(input_file)
    except FileNotFoundError:
        raise ValueError(f"Input file not found: {input_file}")
    except Exception as e:
        raise ValueError(f"Failed to parse CSV: {e}")
    
    # Validate schema
    expected_columns = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
    actual_columns = set(df.columns)
    
    if not expected_columns.issubset(actual_columns):
        missing = expected_columns - actual_columns
        raise ValueError(f"Schema validation failed. Missing columns: {missing}")
    
    # Identify null rows
    null_mask = df["actual_spend"].isna() | (df["actual_spend"] == "")
    null_rows = df[null_mask]
    
    print(f"✓ Dataset loaded: {len(df)} rows, {len(df.columns)} columns")
    print(f"✓ Null rows in actual_spend: {len(null_rows)}")
    if len(null_rows) > 0:
        print("\n  Null row details:")
        for idx, row in null_rows.iterrows():
            print(f"    {row['period']} · {row['ward']} · {row['category']} · Reason: {row['notes']}")
    
    return df


# ============================================================================
# SKILL: compute_growth
# ============================================================================
def compute_growth(df, ward, category, growth_type):
    """
    Calculate MoM or YoY growth for a single ward + category; flag nulls; show formula per row.
    
    Args:
        df (DataFrame): Full dataset from load_dataset
        ward (str): Single ward name
        category (str): Single category name
        growth_type (str): Either 'MoM' or 'YoY'
    
    Returns:
        DataFrame: period, actual_spend, formula_used, growth_value, null_flag, null_reason
    Raises:
        ValueError: If validation fails
    """
    # Enforcement: Refuse if growth_type not specified
    if not growth_type:
        raise ValueError("--growth-type is required. Specify 'MoM' (month-over-month) or 'YoY' (year-over-year).")
    
    if growth_type.upper() not in ["MOM", "YOY"]:
        raise ValueError(f"Invalid growth_type '{growth_type}'. Must be 'MoM' or 'YoY'.")
    
    growth_type = growth_type.upper()
    
    # Filter to single ward + category
    filtered = df[(df["ward"] == ward) & (df["category"] == category)].copy()
    
    if len(filtered) == 0:
        raise ValueError(f"No data found for ward='{ward}' and category='{category}'")
    
    # Sort by period ascending (Jan–Dec 2024)
    filtered = filtered.sort_values("period").reset_index(drop=True)
    
    # Build output table
    results = []
    
    for idx, row in filtered.iterrows():
        period = row["period"]
        actual_spend = row["actual_spend"]
        notes = row["notes"]
        
        result_row = {
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": actual_spend,
            "formula_used": None,
            "growth_value": None,
            "null_flag": False,
            "null_reason": None
        }
        
        # Check if actual_spend is null
        if pd.isna(actual_spend) or actual_spend == "":
            result_row["null_flag"] = True
            result_row["null_reason"] = notes
            result_row["formula_used"] = "N/A (null actual_spend)"
            results.append(result_row)
            continue
        
        # Convert to float for calculation
        try:
            current_spend = float(actual_spend)
        except (ValueError, TypeError):
            result_row["null_flag"] = True
            result_row["null_reason"] = f"Invalid actual_spend value: {actual_spend}"
            result_row["formula_used"] = "N/A (invalid value)"
            results.append(result_row)
            continue
        
        # Calculate growth
        if growth_type == "MOM":
            # Month-over-month: compare to previous month
            if idx == 0:
                # First month has no prior month
                result_row["formula_used"] = "N/A (first period)"
                result_row["growth_value"] = None
            else:
                prior_spend = filtered.iloc[idx - 1]["actual_spend"]
                
                # Check if prior is null
                if pd.isna(prior_spend) or prior_spend == "":
                    result_row["formula_used"] = "N/A (prior period null)"
                    result_row["growth_value"] = None
                else:
                    try:
                        prior_spend = float(prior_spend)
                        growth = (current_spend / prior_spend) - 1
                        result_row["formula_used"] = f"(${current_spend}L / ${prior_spend}L) - 1"
                        result_row["growth_value"] = round(growth * 100, 1)  # Percentage
                    except (ValueError, TypeError):
                        result_row["formula_used"] = "N/A (prior value invalid)"
                        result_row["growth_value"] = None
        
        elif growth_type == "YOY":
            # Year-over-year: compare to 12 months prior (not applicable for full 12-month data)
            # For 2024 data spanning Jan–Dec, YoY would require 2023 data
            result_row["formula_used"] = "N/A (insufficient historical data for YoY)"
            result_row["growth_value"] = None
        
        results.append(result_row)
    
    result_df = pd.DataFrame(results)
    return result_df


# ============================================================================
# MAIN ORCHESTRATION
# ============================================================================
def main():
    parser = argparse.ArgumentParser(
        description="UC-0C: Ward-level budget growth analysis"
    )
    parser.add_argument("--input", required=True, help="Path to input CSV file")
    parser.add_argument("--ward", required=True, help="Single ward name (e.g., 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=True, help="Single category name (e.g., 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", required=False, help="'MoM' or 'YoY' (required; no default)")
    parser.add_argument("--output", required=True, help="Path to output CSV file")
    
    args = parser.parse_args()
    
    try:
        print("\n" + "=" * 70)
        print("UC-0C GROWTH ANALYSIS AGENT")
        print("=" * 70)
        
        # SKILL: load_dataset
        print("\n[STEP 1] Loading and validating dataset...")
        df = load_dataset(args.input)
        
        # Enforcement: Refuse if growth_type not specified
        if not args.growth_type:
            print("\n❌ ERROR: --growth-type is required.")
            print("   Specify 'MoM' (month-over-month) or 'YoY' (year-over-year).")
            sys.exit(1)
        
        # SKILL: compute_growth
        print(f"\n[STEP 2] Computing {args.growth_type} growth for:")
        print(f"   Ward: {args.ward}")
        print(f"   Category: {args.category}")
        
        result_df = compute_growth(df, args.ward, args.category, args.growth_type)
        
        # Display results
        print(f"\n✓ Computed {len(result_df)} rows")
        null_count = result_df["null_flag"].sum()
        if null_count > 0:
            print(f"  ⚠ {null_count} row(s) with null actual_spend (flagged, not computed)")
        
        print("\n[STEP 3] Output table:")
        print(result_df.to_string(index=False))
        
        # Write output CSV
        print(f"\n[STEP 4] Writing output to {args.output}...")
        result_df.to_csv(args.output, index=False)
        print(f"✓ Output written: {args.output}")
        
        print("\n" + "=" * 70)
        print("SUCCESS")
        print("=" * 70 + "\n")
    
    except ValueError as e:
        print(f"\n❌ VALIDATION ERROR: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
