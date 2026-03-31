skills:
  - name: load_dataset
    description: Reads ward_budget.csv, validates required columns, and reports all null actual_spend rows with their notes before returning the DataFrame.
    input: input_path (str) — path to ward_budget.csv.
    output: pandas.DataFrame with columns period, ward, category, budgeted_amount, actual_spend, notes. Prints a null-row report to stdout before returning.
    error_handling: Raises ValueError if required columns are missing. Raises FileNotFoundError if path does not exist. Never silently fills null values — returns them as NaN for the caller to handle explicitly.

  - name: compute_growth
    description: Computes per-period MoM or YoY growth for a single ward + category combination, showing the formula for each row and flagging nulls.
    input: df (DataFrame from load_dataset), ward (str), category (str), growth_type (str — must be "MoM" or "YoY").
    output: list of dicts with keys period, ward, category, actual_spend, growth, formula, notes. Rows with null actual_spend have growth="FLAGGED — null actual_spend" and formula="N/A". Rows where the prior period is null have growth="FLAGGED — prior period is null".
    error_handling: Raises ValueError if ward or category produces no rows. Raises ValueError if growth_type is not "MoM" or "YoY". Never returns a growth figure for a null or unknown-prior row.
