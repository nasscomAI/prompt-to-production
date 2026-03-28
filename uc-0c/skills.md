# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: load_dataset
    description: Reads the budget CSV, validates columns, and reports null count and which rows before returning data.
    input: Path to budget CSV file (string).
    output: List of rows (dict), null row count, and list of null rows with reasons.
    error_handling: If file is missing, columns are invalid, or data is unreadable, returns an error message and empty list.

  - name: compute_growth
    description: Takes ward, category, and growth_type, returns a per-period table with formula shown for each result.
    input: List of rows (dict), ward (string), category (string), growth_type (string: MoM or YoY).
    output: Table (list of dicts) with period, actual_spend, growth, formula, and flags for nulls.
    error_handling: If growth_type is missing, ambiguous, or if aggregation is requested across wards/categories, refuses and outputs an error message. Flags and skips null rows, reporting reasons from notes column.
