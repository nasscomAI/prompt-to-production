skills:
  - name: load_dataset
    description: Reads the budget CSV, validates columns, and identifies all rows with null actual_spend before returning the data.
    input: File path to ward_budget.csv.
    output: A tuple containing the full DataFrame and a list of flagged null rows with reasons.
    error_handling: Reports an error if the file is missing or if mandatory columns (period, ward, category) are malformed.

  - name: compute_growth
    description: Calculates per-period growth for a specific ward and category using the specified growth type (e.g., MoM).
    input: Filter parameters (ward, category, growth_type) and the loaded dataset.
    output: A list of result objects each containing the period, actual spend, growth percentage, and the calculation formula used.
    error_handling: Refuses to compute if multiple wards or categories are selected simultaneously; returns a "Manual Review Required" flag for periods where spend is null, citing the reason from the notes.
