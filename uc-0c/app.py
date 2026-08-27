"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
import pandas as pd
from typing import Dict, Any, List, Tuple, Union

# --- Skills Implementation (as per skills.md guidance) ---

def load_dataset(input_path: str) -> Tuple[pd.DataFrame, List[Dict[str, str]]]:
    """
    Skill: load_dataset
    Description: Reads a CSV file, validates its expected columns, and identifies rows with null 'actual_spend' values.
    Input: input_path (str) - Path to the input CSV file.
    Output: (pd.DataFrame, List[dict]) - Loaded data and list of null row details.
    Error Handling: Raises FileNotFoundError, ValueError. Reports parsing errors.
    """
    expected_columns = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
    null_rows_info = []

    try:
        df = pd.read_csv(input_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found at: {input_path}")
    except pd.errors.EmptyDataError:
        print(f"Warning: Input file is empty at: {input_path}")
        return pd.DataFrame(columns=expected_columns), []
    except Exception as e:
        raise Exception(f"Error reading CSV file {input_path}: {e}")

    # Validate columns
    missing_cols = [col for col in expected_columns if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns in CSV: {', '.join(missing_cols)}")

    # Ensure 'period' is datetime for sorting
    df['period'] = pd.to_datetime(df['period'])
    
    # Identify null 'actual_spend' rows and collect their info
    null_actual_spend_df = df[df['actual_spend'].isnull()]
    for index, row in null_actual_spend_df.iterrows():
        null_rows_info.append({
            'row_number': index + 2, # +2 for 0-based index and header row
            'ward': row['ward'],
            'category': row['category'],
            'period': row['period'].strftime('%Y-%m'),
            'notes': row['notes']
        })
    
    return df, null_rows_info


def compute_growth(
    data: pd.DataFrame, 
    target_ward: str, 
    target_category: str, 
    growth_type: str, 
    null_rows_info: List[Dict[str, str]]
) -> pd.DataFrame:
    """
    Skill: compute_growth
    Description: Calculates Month-over-Month (MoM) growth for a specific ward and category,
                 flagging null values and showing the formula.
    Input: data (pd.DataFrame), target_ward (str), target_category (str),
           growth_type (str), null_rows_info (List[dict]).
    Output: pd.DataFrame - Growth report.
    Error Handling: Returns empty DataFrame if no data, flags nulls.
    """
    if growth_type != "MoM":
        raise ValueError(f"Unsupported growth type: '{growth_type}'. Only 'MoM' is supported.")

    # Filter for the specific ward and category
    filtered_df = data[
        (data['ward'] == target_ward) & 
        (data['category'] == target_category)
    ].sort_values(by='period').copy() # .copy() to avoid SettingWithCopyWarning

    if filtered_df.empty:
        return pd.DataFrame(columns=[
            'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 
            'growth_percentage', 'formula', 'notes', 'flag'
        ])

    # Initialize new columns
    filtered_df['growth_percentage'] = pd.NA
    filtered_df['formula'] = pd.NA
    filtered_df['flag'] = ""

    # Populate flags for nulls from the original null_rows_info
    for null_info in null_rows_info:
        # Match by ward, category, and period
        match_idx = filtered_df[
            (filtered_df['ward'] == null_info['ward']) &
            (filtered_df['category'] == null_info['category']) &
            (filtered_df['period'] == pd.to_datetime(null_info['period']))
        ].index
        if not match_idx.empty:
            filtered_df.loc[match_idx, 'flag'] = f"NULL_ACTUAL_SPEND: {null_info['notes']}"
            filtered_df.loc[match_idx, 'growth_percentage'] = "NULL" # As per README
            filtered_df.loc[match_idx, 'formula'] = "N/A" # As per README


    # Compute MoM growth for non-null actual_spend values
    # Use .shift(1) to get the previous month's actual_spend
    # Ensure calculation only happens if actual_spend is not null for current AND previous month
    for i in range(1, len(filtered_df)):
        current_row = filtered_df.iloc[i]
        prev_row = filtered_df.iloc[i-1]

        if pd.notna(current_row['actual_spend']) and pd.notna(prev_row['actual_spend']):
            current_spend = current_row['actual_spend']
            prev_spend = prev_row['actual_spend']

            if prev_spend != 0: # Avoid division by zero
                growth = ((current_spend - prev_spend) / prev_spend) * 100
                formula_str = f"({current_spend:.1f} - {prev_spend:.1f}) / {prev_spend:.1f} * 100"
                filtered_df.loc[filtered_df.index[i], 'growth_percentage'] = f"{growth:+.1f}%"
                filtered_df.loc[filtered_df.index[i], 'formula'] = formula_str
            else:
                filtered_df.loc[filtered_df.index[i], 'growth_percentage'] = "N/A (Prev Spend Zero)"
                filtered_df.loc[filtered_df.index[i], 'formula'] = f"({current_spend:.1f} - {prev_spend:.1f}) / {prev_spend:.1f} * 100"
        elif pd.notna(current_row['actual_spend']) and pd.isna(prev_row['actual_spend']):
             # If previous month was null, current month cannot compute MoM
             filtered_df.loc[filtered_df.index[i], 'growth_percentage'] = "N/A (Prev Month NULL)"
             filtered_df.loc[filtered_df.index[i], 'formula'] = "N/A"

    # For the very first month, MoM growth is undefined
    if not filtered_df.empty:
        if filtered_df.loc[filtered_df.index[0], 'flag'] == "": # Don't overwrite existing null flag
             filtered_df.loc[filtered_df.index[0], 'growth_percentage'] = "N/A (First Month)"
             filtered_df.loc[filtered_df.index[0], 'formula'] = "N/A"

    # Convert period back to YYYY-MM string for output
    filtered_df['period'] = filtered_df['period'].dt.strftime('%Y-%m')

    # Select and order columns for final output
    output_columns = [
        'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 
        'growth_percentage', 'formula', 'notes', 'flag'
    ]
    return filtered_df[output_columns]


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input",  required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward",   required=False, help="Specific ward to analyze (e.g., 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=False, help="Specific category to analyze (e.g., 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", required=False, help="Type of growth calculation (e.g., 'MoM' for Month-over-Month)")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    # --- Enforcement Rules Check ---
    # 1. Never aggregate across wards or categories unless explicitly instructed — refuse if asked
    if args.ward is None or args.category is None: # Assuming None implies "all" or "any"
        print("Enforcement Rule Violation: Cannot aggregate across wards or categories without explicit instruction.")
        print("Please specify a '--ward' and '--category' argument (e.g., '--ward \"Ward 1 – Kasba\" --category \"Roads & Pothole Repair\"').")
        return
    # This check also covers the "Any | Any | Any | n/a | All-ward aggregation → system must REFUSE" from README.

    # 4. If `--growth-type` not specified — refuse and ask, never guess
    if args.growth_type is None:
        print("Enforcement Rule Violation: '--growth-type' not specified.")
        print("Please specify a growth type (e.g., '--growth-type MoM').")
        return
    
    if args.growth_type != "MoM":
        print(f"Enforcement Rule Violation: Unsupported growth type '{args.growth_type}'. Only 'MoM' is currently supported.")
        return


    try:
        data, null_rows_summary = load_dataset(args.input)
        
        if data.empty:
            print("No data loaded or data is empty after initial processing. Exiting.")
            return

        print(f"Loaded {len(data)} rows from {args.input}.")
        if null_rows_summary:
            print(f"Detected {len(null_rows_summary)} rows with null 'actual_spend':")
            for null_info in null_rows_summary:
                print(f"  - Period: {null_info['period']}, Ward: {null_info['ward']}, Category: {null_info['category']}, Reason: {null_info['notes']}")
        else:
            print("No null 'actual_spend' values detected.")
            
        growth_output_df = compute_growth(
            data, 
            args.ward, 
            args.category, 
            args.growth_type, 
            null_rows_summary # Pass null info to compute_growth for flagging
        )

        if growth_output_df.empty:
            print(f"No data found for Ward: '{args.ward}', Category: '{args.category}'. Output file will be empty.")
        else:
            growth_output_df.to_csv(args.output, index=False)
            print(f"Done. Growth analysis written to {args.output}")

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except ValueError as e:
        print(f"Configuration Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()


