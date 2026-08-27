skills:
  - name: load_dataset
    description: Reads ward_budget.csv, validates required columns, and identifies null actual_spend rows.
    input: Path to ward_budget.csv.
    output: List of normalized row dictionaries and a list of null actual_spend rows with notes.
    error_handling: Raise a clear error when required columns are missing or the file cannot be read.

  - name: compute_growth
    description: Computes explicit MoM growth for one ward and one category without all-ward aggregation.
    input: Dataset rows, ward name, category name, and growth_type.
    output: Per-period table with actual spend, previous spend, growth percent, formula, status, and notes.
    error_handling: Refuse missing ward/category/growth_type; flag null current or previous values instead of computing.
