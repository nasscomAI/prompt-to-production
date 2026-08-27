skills:
  - name: load_dataset
    description: Reads CSV, validates columns, reports null count and which rows before returning.
    input: Filepath to CSV dataset.
    output: Parsed dataset, null row count, and list of specific rows containing null actual_spend values.
    error_handling: Halts execution if required columns are missing or if file cannot be read.

  - name: compute_growth
    description: Takes ward, category, and growth_type, and returns per-period table with formula shown.
    input: Dataset, specific ward, specific category, and required growth_type (e.g., MoM).
    output: Per-period table containing computed growth value and a string showing the formula used.
    error_handling: Refuses and prompts user if growth_type is not specified, or if cross-ward/cross-category aggregation is requested without permission.
