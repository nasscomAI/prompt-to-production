"""
UC-0C app.py — Budget Growth Analyst
Implements load_dataset and compute_growth skills per agents.md and skills.md.
Enforces: no cross-ward/category aggregation, null flagging, formula display.
"""
import argparse
import pandas as pd
import sys
from pathlib import Path

# Known null rows from requirements
KNOWN_NULLS = [
    {"period": "2024-03", "ward": "Ward 2 – Shivajinagar", "category": "Drainage & Flooding"},
    {"period": "2024-07", "ward": "Ward 4 – Warje", "category": "Roads & Pothole Repair"},
    {"period": "2024-11", "ward": "Ward 1 – Kasba", "category": "Waste Management"},
    {"period": "2024-08", "ward": "Ward 3 – Kothrud", "category": "Parks & Greening"},
    {"period": "2024-05", "ward": "Ward 5 – Hadapsar", "category": "Streetlight Maintenance"},
]

def load_dataset(file_path):
    """
    Load and validate CSV file. Return metadata about dataset.
    Enforces: Schema validation, null reporting, ward/category inventory.
    """
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"ERROR: File not found: {file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Could not read file {file_path}: {e}")
        sys.exit(1)
    
    # Validate schema
    required_cols = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
    actual_cols = set(df.columns)
    if not required_cols.issubset(actual_cols):
        missing = required_cols - actual_cols
        print(f"ERROR: Missing columns in CSV: {missing}")
        print(f"Expected: {required_cols}")
        print(f"Got: {actual_cols}")
        sys.exit(1)
    
    # Report null rows
    print("\n=== NULL ROWS REPORT ===")
    null_rows = df[df["actual_spend"].isna()][["period", "ward", "category", "notes"]]
    if len(null_rows) > 0:
        for idx, row in null_rows.iterrows():
            print(f"  {row['period']} · {row['ward']} · {row['category']}")
            print(f"    Reason: {row['notes']}")
    else:
        print("  No null rows found (expected 5)")
    
    # Inventory wards and categories
    wards = sorted(df["ward"].unique().tolist())
    categories = sorted(df["category"].unique().tolist())
    
    return {
        "valid": True,
        "df": df,
        "row_count": len(df),
        "null_count": len(null_rows),
        "wards": wards,
        "categories": categories,
    }

def compute_growth(df, ward, category, growth_type):
    """
    Compute MoM or YoY growth for specific ward+category.
    Enforces: parameter validation, formula display, null handling.
    """
    # Validation: growth_type
    if growth_type not in ["MoM", "YoY"]:
        print(f"ERROR: Invalid growth_type '{growth_type}'. Must be 'MoM' or 'YoY'")
        sys.exit(1)
    
    # Validation: ward exists
    all_wards = df["ward"].unique().tolist()
    if ward not in all_wards:
        print(f"ERROR: Ward '{ward}' not found in data.")
        print(f"Valid wards: {all_wards}")
        sys.exit(1)
    
    # Validation: category exists
    all_categories = df["category"].unique().tolist()
    if category not in all_categories:
        print(f"ERROR: Category '{category}' not found in data.")
        print(f"Valid categories: {all_categories}")
        sys.exit(1)
    
    # Filter to ward+category
    filtered = df[(df["ward"] == ward) & (df["category"] == category)].copy()
    
    if len(filtered) == 0:
        print(f"ERROR: No data for ward='{ward}' and category='{category}'")
        sys.exit(1)
    
    # Sort by period
    filtered = filtered.sort_values("period").reset_index(drop=True)
    
    # Compute growth
    results = []
    
    for idx, row in filtered.iterrows():
        period = row["period"]
        actual_spend = row["actual_spend"]
        
        if pd.isna(actual_spend):
            # Null value — flag with reason
            results.append({
                "period": period,
                "actual_spend": None,
                "growth_value": None,
                "growth_formula": "N/A",
                "null_reason": row["notes"],
            })
            continue
        
        if idx == 0:
            # First period — no growth to compute
            results.append({
                "period": period,
                "actual_spend": actual_spend,
                "growth_value": None,
                "growth_formula": "N/A (first period)",
                "null_reason": None,
            })
            continue
        
        # Get previous row for growth calculation
        if growth_type == "MoM":
            prev_idx = idx - 1
            prev_spend = filtered.iloc[prev_idx]["actual_spend"]
            
            if pd.isna(prev_spend):
                # Previous period is null — cannot compute
                results.append({
                    "period": period,
                    "actual_spend": actual_spend,
                    "growth_value": None,
                    "growth_formula": "N/A (previous period null)",
                    "null_reason": None,
                })
                continue
            
            # Compute MoM growth
            growth_pct = ((actual_spend - prev_spend) / prev_spend) * 100
            sign = "+" if growth_pct >= 0 else ""
            growth_value = f"{sign}{growth_pct:.1f}%"
            formula = f"({actual_spend} − {prev_spend}) / {prev_spend}"
            
        elif growth_type == "YoY":
            # YoY: look back 12 periods
            prev_idx = idx - 12
            if prev_idx < 0:
                # Not enough history for YoY
                results.append({
                    "period": period,
                    "actual_spend": actual_spend,
                    "growth_value": None,
                    "growth_formula": "N/A (insufficient history for YoY)",
                    "null_reason": None,
                })
                continue
            
            prev_spend = filtered.iloc[prev_idx]["actual_spend"]
            if pd.isna(prev_spend):
                results.append({
                    "period": period,
                    "actual_spend": actual_spend,
                    "growth_value": None,
                    "growth_formula": "N/A (YoY prior period null)",
                    "null_reason": None,
                })
                continue
            
            # Compute YoY growth
            growth_pct = ((actual_spend - prev_spend) / prev_spend) * 100
            sign = "+" if growth_pct >= 0 else ""
            growth_value = f"{sign}{growth_pct:.1f}%"
            formula = f"({actual_spend} − {prev_spend}) / {prev_spend} [YoY]"
        
        results.append({
            "period": period,
            "actual_spend": actual_spend,
            "growth_value": growth_value,
            "growth_formula": formula,
            "null_reason": None,
        })
    
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Analyst")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name (e.g., 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=True, help="Budget category name")
    parser.add_argument("--growth-type", required=True, help="'MoM' or 'YoY'")
    parser.add_argument("--output", required=True, help="Output CSV file path")
    
    args = parser.parse_args()
    
    # Load and validate dataset
    print("Loading dataset...")
    dataset = load_dataset(args.input)
    
    # Compute growth
    print(f"\nComputing {args.growth_type} growth for:")
    print(f"  Ward: {args.ward}")
    print(f"  Category: {args.category}")
    
    results = compute_growth(dataset["df"], args.ward, args.category, args.growth_type)
    
    # Convert results to DataFrame and save
    results_df = pd.DataFrame(results)
    results_df.to_csv(args.output, index=False)
    
    print(f"\nResults written to {args.output}")
    print("\nSample output:")
    print(results_df.to_string(max_rows=5))

if __name__ == "__main__":
    main()
