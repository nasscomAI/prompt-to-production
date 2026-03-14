# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: load_dataset
    description: Reads CSV, validates columns, reports null count and which rows before returning.
    input: File path (string) to the CSV file.
    output: Parsed data structure (e.g., list of dicts) with validation report including null details.
    error_handling: If columns are missing or invalid, return error details and empty data.

  - name: compute_growth
    description: Takes ward + category + growth_type, returns per-period table with formula shown.
    input: Ward (string), category (string), growth_type (string, e.g., 'MoM'), and loaded dataset.
    output: CSV-like table with period, actual_spend, growth, formula, and flags for nulls.
    error_handling: If ward/category not found or growth_type invalid, return error message; flag nulls explicitly.
