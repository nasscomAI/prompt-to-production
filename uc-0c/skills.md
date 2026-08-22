# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates columns, and reports null count and rows before returning.
    input: Path to ward_budget.csv (string).
    output: Structured dataset with rows containing period, ward, category, budgeted_amount, actual_spend, notes.
    error_handling: If file is missing, unreadable, or columns invalid, return "INVALID_INPUT". If null values are found, list them explicitly with reasons before proceeding.

  - name: compute_growth
    description: Computes growth for a given ward, category, and growth_type, producing a per-period table with formula shown.
    input: Dataset from load_dataset, plus ward (string), category (string), growth_type (string).
    output: CSV table with columns: period, ward, category, actual_spend, growth_value, formula, flag.
    error_handling: If growth_type is missing, refuse and request explicit type. If null actual_spend rows are encountered, flag them with reason from notes and skip computation for those rows.
