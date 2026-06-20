# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

    output: [What does it return? Type and format.]
  - name: load_dataset
    description: Reads the ward budget CSV, validates the required columns, and identifies null actual_spend rows.
    input: A CSV file path.
    output: Dataset metadata containing parsed rows, unique wards and categories, null count, and null row details.
    error_handling: Raises an error when required columns are missing or the file structure is invalid.
    output: [Type and format]
  - name: compute_growth
    description: Filters the dataset to one ward and one category and computes per-period MoM or YoY growth with formula output.
    input: Parsed dataset plus exact ward, exact category, and explicit growth_type.
    output: A per-period table with actual spend, comparison values, growth result, status, formula, and notes.
    error_handling: Refuses aggregation, refuses missing or unsupported growth_type, and flags current or comparison nulls instead of computing through them.
