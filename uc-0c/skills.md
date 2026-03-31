skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates the required columns, and identifies all null rows before returning the data.
    input: Path to the budget CSV file (string).
    output: A list of records or a dataframe containing the budget data, and a report of null count/rows.
    error_handling: Refuse if the file is missing or if mandatory columns (period, ward, category, budgeted_amount, actual_spend) are absent.

  - name: compute_growth
    description: Calculates period-over-period growth for a specific ward and category based on the specified growth type (MoM/YoY).
    input: ward (string), category (string), growth_type (string), dataset (list/dataframe).
    output: A table of growth results including the period, actual spend, growth percentage, and the formula used.
    error_handling: Refuse if growth_type is missing or if the request implies unauthorized aggregation. Flag null rows and provide the reason from notes.
