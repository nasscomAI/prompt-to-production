# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: load_dataset
    description: Read the ward budget CSV, validate required columns, and report any null rows before returning structured records.
    input: Path string to `ward_budget.csv`.
    output: List of dictionaries representing each row, with parsed numeric fields and null markers.
    error_handling: Raises a descriptive error if required columns are missing or input rows are malformed.

  - name: compute_growth
    description: Compute per-period growth for a single ward and category using the requested growth type.
    input: Filtered dataset rows, ward string, category string, growth_type string (`MoM` or `YoY`).
    output: List of dictionaries containing period, actual_spend, previous_period, growth_pct, formula, status, and notes.
    error_handling: Returns rows with a not-computed status when prior values are missing or null, and refuses if ward/category selection is ambiguous.
