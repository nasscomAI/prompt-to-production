# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

    output: [What does it return? Type and format.]
  - name: load_dataset
    description: Loads the ward budget CSV, validates required columns, and identifies null actual_spend rows with reasons.
    input: Path to ward_budget.csv.
    output: Parsed row list plus null-row diagnostics.
    error_handling: Raises clear validation errors for missing files, missing columns, or malformed numeric data.
    output: [Type and format]
  - name: compute_growth
    description: Computes MoM or YoY growth for one ward and one category over time.
    input: Parsed dataset, ward string, category string, and growth type.
    output: Per-period rows with actual spend, growth value, and formula.
    error_handling: Refuses aggregate or unsupported requests and flags rows where growth cannot be computed due to null or missing prior values.
