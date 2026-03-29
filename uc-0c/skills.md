# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: load_dataset
    description: reads CSV, validates columns, reports null count and which rows before returning.
    input: String path to the dataset CSV file.
    output: A validated dataset object/list of dictionaries.
    error_handling: System exits if dataset fails validation or is missing.

  - name: compute_growth
    description: takes ward + category + growth_type, returns per-period table with formula shown.
    input: Validated dataset list, String ward, String category, String growth_type.
    output: List of rows representing the final growth table with formulas shown.
    error_handling: Refuses to compute if growth_type is missing or if cross-ward/cross-category aggregation is requested.
