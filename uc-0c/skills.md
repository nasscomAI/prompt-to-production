# skills.md

skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates required columns, reports null actual_spend rows, and returns structured rows.
    input: Path to ward_budget.csv.
    output: Tuple containing a list of data rows and a list of null actual_spend row records.
    error_handling: Raises an error if required columns are missing or if actual_spend contains invalid values.

  - name: compute_growth
    description: Computes per-period growth for a given ward/category and growth type, including formula and null handling.
    input: Structured dataset rows, ward name, category name, growth type.
    output: List of output rows with period, actual_spend, formula, growth_pct, and note.
    error_handling: Raises an error if the requested ward/category combination is missing or if the growth type is unsupported.
