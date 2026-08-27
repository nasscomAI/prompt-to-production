# skills.md

skills:
  - name: load_dataset
    description: Reads the budget CSV, validates column integrity, and performs an initial scan to identify and report null count and specific null rows.
    input: Path to the `ward_budget.csv` file.
    output: List of row dictionaries representing the dataset, or an error if columns are missing.
    error_handling: Raises an error if required columns (period, ward, category, budgeted_amount, actual_spend) are missing or if the file cannot be read.

  - name: compute_growth
    description: Filters data for a specific ward and category, then calculates MoM or YoY growth, preserving null flags and formulas.
    input: Dataset from `load_dataset`, `ward` name, `category` name, and `growth_type` (MoM or YoY).
    output: A list of result dictionaries including `period`, `actual_spend`, `growth_value`, and `formula`.
    error_handling: Returns a refusal if asked to aggregate or if `growth_type` is missing. Flags null rows with their reason from notes.
