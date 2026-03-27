# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: load_dataset
    description: Reads the CSV, validates columns, and reports null count and which rows before returning the data.
    input: Path to the CSV file.
    output: Tuple of (data as list of dicts, null row info as list of dicts).
    error_handling: Raises error if columns are missing or file cannot be read; reports and flags nulls.

  - name: compute_growth
    description: Computes growth for a given ward, category, and growth_type, returning a per-period table with formula shown.
    input: Data as list of dicts, ward (string), category (string), growth_type (string: MoM or YoY).
    output: List of dicts, each with period, actual_spend, growth, formula, and null flag/reason if applicable.
    error_handling: Refuses if growth_type is not specified, or if asked to aggregate across wards/categories without explicit instruction; flags and explains nulls.
