skills:
  - name: load_dataset
    description: Reads a CSV file containing ward budget data, validates the presence of required columns (period, ward, category, budgeted_amount, actual_spend, notes), and reports the count of null values in actual_spend along with details of which specific rows are null before returning the dataset.
    input: File path to the CSV file (string, e.g., '../data/budget/ward_budget.csv').
    output: A pandas DataFrame containing the loaded data with validated columns, plus a dictionary report with null count and list of null row details (including period, ward, category, and notes).
    error_handling: If required columns are missing, raises a ValueError with details of missing columns; if nulls are detected in actual_spend, explicitly reports them with reasons from notes instead of silently handling or ignoring them, preventing silent null handling failure mode.
  - name: compute_growth
    description: Computes growth rates (MoM or YoY) for a specified ward and category from the loaded dataset, returning a per-period table that includes actual spend, growth percentages, and the formula used for each calculation.
    input: Ward name (string), category name (string), growth_type (string, e.g., 'MoM' or 'YoY'), and the loaded dataset (pandas DataFrame).
    output: A pandas DataFrame with columns for period, actual_spend, growth_percentage, formula, and null_flag (with reason if applicable), ensuring per-ward per-category granularity without aggregation.
    error_handling: If ward or category is not found in the dataset, raises a ValueError; if growth_type is invalid or not specified, refuses to proceed and prompts for clarification instead of guessing; if null values are present, flags them explicitly with notes reasons and skips growth computation for those rows, avoiding formula assumption and wrong aggregation failure modes.