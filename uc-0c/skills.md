# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: load_dataset
    description: Reads a CSV file, validates columns, reports null count and which rows have null actual_spend before returning the data.
    input: File path to the budget CSV (string).
    output: List of dictionaries representing the CSV rows.
    error_handling: If file not found or invalid CSV, reports error and returns empty list.

  - name: compute_growth
    description: Takes ward, category, and growth_type, filters data, computes per-period growth with formulas shown, flags nulls.
    input: Data list, ward (string), category (string), growth_type (string), output_path (string).
    output: Writes a CSV file with period, actual_spend, mom_growth, formula, flag columns.
    error_handling: Refuses if growth_type not MoM or no data for ward/category; flags null rows and skips computation.
