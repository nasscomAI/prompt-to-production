# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: load_dataset
    description: Reads budget CSV, validates columns, and reports null count and reasons.
    input: file_path (string)
    output: A list of dicts representing the rows
    error_handling: If critical columns are missing, raise ValueError.

  - name: compute_growth
    description: Takes ward, category, and growth_type, returns per-period table with formula shown.
    input: ward (string), category (string), growth_type (string), data (list)
    output: A list of dicts with keys — period, actual_spend, growth, formula, status
    error_handling: If growth_type is invalid, return an error message.
