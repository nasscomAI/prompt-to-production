# skills.md

skills:
  - name: load_dataset
    description: Reads a CSV file containing ward budget data, validates required columns, identifies and reports all null actual_spend values with their reasons before returning the dataset.
    input: File path (string) pointing to a .csv file with required columns (period, ward, category, budgeted_amount, actual_spend, notes).
    output: Dictionary containing 'data' (pandas DataFrame or list of dictionaries), 'null_count' (integer count of null actual_spend values), 'null_details' (list of dictionaries with period, ward, category, and reason for each null), 'wards' (list of unique ward names), 'categories' (list of unique category names), and 'periods' (list of unique period values).
    error_handling: Returns None with error message if file does not exist, cannot be read, or is missing required columns (period, ward, category, budgeted_amount, actual_spend, notes). Raises ValueError if file path is empty or CSV structure is invalid. Always reports null count upfront — zero or non-zero.

  - name: compute_growth
    description: Computes growth metrics (MoM or YoY) for a specific ward and category combination, returning a per-period table with explicit formula display and null flagging.
    input: Dictionary with keys 'data' (dataset from load_dataset), 'ward' (string - specific ward name), 'category' (string - specific category name), 'growth_type' (string - must be exactly 'MoM' or 'YoY'), and 'null_details' (list from load_dataset).
    output: List of dictionaries where each entry contains 'period', 'actual_spend', 'growth_value' (percentage or NULL_FLAGGED), 'formula_used' (explicit formula string like "MoM = (19.7 - 14.8) / 14.8 × 100%"), and 'note' (explanation for null or non-computable periods). Returns structured table ready for CSV export.
    error_handling: Refuses to proceed and returns error if growth_type is not 'MoM' or 'YoY'. Refuses if ward or category not found in dataset. Flags periods with null actual_spend as NULL_FLAGGED with reason from notes. Returns error for first period in MoM (no previous period) or any period without previous year data in YoY.
