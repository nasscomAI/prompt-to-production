# skills.md

skills:
  - name: load_dataset
    description: Reads the budget CSV, validates columns, and explicitly reports the total null count and identifies which specific rows have null values before returning the data.
    input: File path to the budget CSV.
    output: Parsed dataset structure along with a manifest of null rows (including the notes column for context).
    error_handling: Return an error if required columns (period, ward, category, budgeted_amount, actual_spend, notes) are missing or malformed.

  - name: compute_growth
    description: Calculates the specified growth metric (e.g., MoM or YoY) for a specific ward and category, returning a per-period table that includes the explicit formula used for each calculation.
    input: Filtered dataset by ward and category, and the growth_type string.
    output: A per-period table showing actual spend, computed growth, and the formula used for each row.
    error_handling: Return an error if the growth_type is missing or invalid, or if an attempt is made to compute growth on a flagged null row.
