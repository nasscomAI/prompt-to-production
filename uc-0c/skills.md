# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: load_dataset
    description: Read the ward budget CSV, validate required columns, and identify null actual_spend rows.
    input: Path to the budget CSV file.
    output: A list of validated rows with parsed period, ward, category, budgeted_amount, actual_spend, and notes.
    error_handling: If the CSV is missing required columns or rows are malformed, raise a descriptive error and do not compute growth.

  - name: compute_growth
    description: Compute growth for the requested ward, category, and growth type, while flagging null rows.
    input: Validated dataset rows, ward name, category name, and growth type (MoM or YoY).
    output: A per-period table with actual spend, growth result, formula, and null flags when applicable.
    error_handling: If growth_type is missing or unsupported, refuse and ask for an explicit growth_type.
