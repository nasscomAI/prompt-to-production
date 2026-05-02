# skills.md

skills:
  - name: load_dataset
    description: Reads CSV, validates columns, and reports null count and which rows before returning.
    input: File path to the dataset (string).
    output: Loaded dataset (DataFrame), total null count, and a list of rows containing nulls.
    error_handling: Raise an error if the file is missing. Flag any missing required columns.

  - name: compute_growth
    description: Takes ward + category + growth_type, returns per-period table with formula shown.
    input: Loaded dataset (DataFrame), ward (string), category (string), growth_type (string).
    output: Per-period table containing the period, growth result, and the explicit formula used.
    error_handling: Flag null rows before computing. Refuse and prompt if growth_type is missing or invalid.
