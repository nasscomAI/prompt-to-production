"""
UC-0C — Budget Growth Analyst
This module implements the budget growth calculation and null handling logic.
"""
import pandas as pd
import numpy as np

def load_dataset(file_path):
    """
    Skill: load_dataset
    Reads CSV, validates columns, and identifies null rows.
    """
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        raise ValueError(f"Could not read CSV: {e}")

    required_columns = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    # Identify null rows for reporting/validation
    null_mask = df['actual_spend'].isna()
    null_rows = df[null_mask].copy()
    
    return df, null_rows

def compute_growth(df, ward, category, growth_type):
    """
    Skill: compute_growth
    Calculates MoM growth for a specific ward and category.
    Enforces no aggregation and handles null values.
    """
    if not growth_type:
        # Enforcement Rule 4: If --growth-type not specified — refuse and ask, never guess
        raise ValueError("Growth type not specified. Please provide --growth-type (e.g., MoM).")
    
    if growth_type != "MoM":
        # Based on README, MoM is the expected type for this UC.
        raise ValueError(f"Growth type '{growth_type}' is not supported. Only MoM is supported.")

    # Enforcement Rule 1: Never aggregate across wards or categories unless explicitly instructed
    # Filter strictly for the requested ward and category.
    filtered_df = df[(df['ward'] == ward) & (df['category'] == category)].copy()
    
    if filtered_df.empty:
        raise ValueError(f"No data found for ward='{ward}' and category='{category}'. Refusing to aggregate.")

    # Sort by period to ensure chronological growth calculation
    filtered_df = filtered_df.sort_values('period')

    results = []
    prev_spend = None
    
    for _, row in filtered_df.iterrows():
        period = row['period']
        current_spend = row['actual_spend']
        notes = row['notes']
        
        result_row = {
            "Ward": ward,
            "Category": category,
            "Period": period,
            "Actual Spend (₹ lakh)": current_spend if not pd.isna(current_spend) else "NULL",
            "MoM Growth": "n/a",
            "Formula": "n/a"
        }

        # Enforcement Rule 2: Flag every null row before computing
        if pd.isna(current_spend):
            result_row["MoM Growth"] = "FLAGGED"
            result_row["Formula"] = f"NULL detected: {notes if pd.notna(notes) else 'No notes provided'}"
        elif prev_spend is None or pd.isna(prev_spend):
            # Cannot calculate MoM if current is first month or previous was null
            if prev_spend is None:
                result_row["Formula"] = "First month in series — no previous data"
            else:
                result_row["Formula"] = "Previous month was NULL — cannot compute MoM"
        else:
            # Calculate MoM Growth
            # Formula: (Current - Previous) / Previous
            growth = (current_spend - prev_spend) / prev_spend
            growth_pct = growth * 100
            result_row["MoM Growth"] = f"{'+' if growth_pct >= 0 else ''}{growth_pct:.1f}%"
            # Enforcement Rule 3: Show formula used in every output row alongside the result
            result_row["Formula"] = f"({current_spend} - {prev_spend}) / {prev_spend}"

        results.append(result_row)
        prev_spend = current_spend

    return results

def process_analysis(input_path, output_path, ward, category, growth_type):
    """
    Orchestration logic following agents.md enforcement rules.
    """
    # 1. Load and validate
    df, null_rows = load_dataset(input_path)
    
    # 2. Compute growth
    results = compute_growth(df, ward, category, growth_type)
    
    # 3. Write output
    results_df = pd.DataFrame(results)
    results_df.to_csv(output_path, index=False)
    
    return len(results)
