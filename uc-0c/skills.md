skills:
  - name: load_dataset
    description: reads CSV, validates columns, reports null count and which rows before returning.
    input: File path to the dataset (string).
    output: Validated dataset table and a summary report of nulls rows (data structure).
    error_handling: Handles missing files or incorrect columns by returning a clear error specifying the expected dataset structure.

  - name: compute_growth
    description: takes ward + category + growth_type, returns per-period table with formula shown.
    input: Ward name (string), category name (string), and growth type (string, e.g., 'MoM', 'YoY').
    output: Per-period table of computed growth including the formula used in every output row (data structure).
    error_handling: Refuses to compute and asks user if growth type is not specified or if aggregation across wards/categories is requested. Flags rows with null spend.
