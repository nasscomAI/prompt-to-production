skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates the expected columns, and performs a strict initial audit for null values.
    input: The absolute path to the budget CSV file.
    output: A validated dataset structure, and an explicit report of the total null count and the specific rows where 'actual_spend' is null.
    error_handling: If expected columns are missing or the file is unreadable, raise a critical error and refuse to proceed. Must explicitly flag nulls rather than ignoring, zeroing, or interpolating them.

  - name: compute_growth
    description: Calculates the specified growth metric for a strictly defined ward and category over a chronological period.
    input: The validated dataset, a target 'ward' string, a target 'category' string, and an explicit 'growth_type' string.
    output: A per-period table containing the period, actual spend, calculated growth, and the explicit mathematical formula used.
    error_handling: Refuses to compute if 'growth_type' is missing or unknown. If an 'actual_spend' value is null for a given period or its prior period required for the formula, it must flag the row with the reason from 'notes' and skip computation for that period, explicitly refusing to interpolate.
