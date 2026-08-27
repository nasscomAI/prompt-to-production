# skills.md

skills:
  - name: load_dataset
    description: Reads the budget CSV, validates essential columns, and reports the null count along with specific null rows (from actual_spend) before returning the dataset.
    input: File path string to `ward_budget.csv`.
    output: A validated dataset object (e.g., DataFrame) and a summary report of null entries.
    error_handling: Refuses if required columns are missing or file is inaccessible.

  - name: compute_growth
    description: Calculates per-period growth (MoM/YoY) for a specific ward and category, ensuring the formula used is returned alongside each result.
    input: A combination of ward name, budget category, and growth_type (MoM or YoY).
    output: A per-period table (CSV format) containing the growth calculation and the explicit formula used.
    error_handling: Refuses if --growth-type is missing or if requested to aggregate across wards/categories.
