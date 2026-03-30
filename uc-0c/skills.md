skills:
  - name: load_dataset
    description: Reads a CSV file, validates its expected columns, and identifies rows with null 'actual_spend' values.
    input:
      - name: input_path
        type: string
        format: Path to the input CSV file (e.g., "../data/budget/ward_budget.csv").
    output:
      type: tuple
      format: A tuple containing (DataFrame, List[dict]). The DataFrame holds the loaded data. The list contains dictionaries, each detailing a null row: {'row_number': int, 'ward': str, 'category': str, 'period': str, 'notes': str}.
    error_handling: Raises FileNotFoundError if the path is invalid. Raises ValueError if essential columns are missing. Logs and skips rows that cannot be parsed, returning partial data and reporting parsing errors.

  - name: compute_growth
    description: Calculates Month-over-Month (MoM) growth for a specific ward and category, flagging null values and showing the formula.
    input:
      - name: data
        type: pandas.DataFrame
        format: The loaded budget data containing 'period', 'ward', 'category', 'budgeted_amount', 'actual_spend'.
      - name: target_ward
        type: string
        format: The specific ward to filter by (e.g., "Ward 1 – Kasba").
      - name: target_category
        type: string
        format: The specific category to filter by (e.g., "Roads & Pothole Repair").
      - name: growth_type
        type: string
        format: The type of growth to compute (e.g., "MoM"). Currently only "MoM" is supported.
      - name: null_rows_info
        type: List[dict]
        format: A list of dictionaries, each detailing a null row, as produced by 'load_dataset'.
    output:
      type: pandas.DataFrame
      format: A DataFrame with columns: 'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'growth_percentage', 'formula', 'notes', 'flag'. Includes MoM growth, formula, and flags for nulls.
    error_handling: Returns an empty DataFrame if no data matches the filters. For rows with null 'actual_spend', it sets 'growth_percentage' to NULL, 'formula' to N/A, and populates a 'flag' column with the reason from 'notes'. Raises ValueError if 'growth_type' is not supported.

