skills:
  - name: load_dataset
    description: Reads ward_budget.csv and validates that it contains the expected 300 rows and identifies the 5 null rows for auditing.
    input: CSV file path.
    output: List of row dictionaries.
    error_handling: Flags a system warning if any month is missing for a ward/category pair.

  - name: compute_growth
    description: Performs MoM or YoY growth calculations for a specific ward and category, enforcing precision and null-reason reporting.
    input: Filtered data list and growth_type string.
    output: A list of result dictionaries with 'period', 'current_spend', 'growth_rate', and 'formula'.
    error_handling: If actual_spend is blank, maps the 'notes' column to the 'growth_rate' field.
