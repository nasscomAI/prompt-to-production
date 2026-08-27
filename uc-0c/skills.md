# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: load_dataset
    description: Reads the budget CSV, validates columns, and identifies all rows with null actual_spend values.
    input: Path to the budget CSV file.
    output: A list of dictionaries (rows) and a report of identified nulls.
    error_handling: Refuse if columns are missing or if the file cannot be read.

  - name: compute_growth
    description: Calculates growth (MoM or YoY) for a specific ward and category, preserving null flags and showing formulas.
    input: Dataset, ward name, category name, and growth type.
    output: A table (list of dicts) with calculated growth, formulas, and null notes.
    error_handling: Refuse if ward or category are not found, or if growth_type is missing.
