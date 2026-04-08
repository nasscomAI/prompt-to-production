skills:
  - name: load_dataset
    description: reads CSV, validates columns, reports null count and which rows before returning.
    input: File path to the CSV dataset (string).
    output: Validated dataset with a report of null values and their corresponding rows (data structure + text).
    error_handling: If file is missing or required columns are absent, raise an error and halt.

  - name: compute_growth
    description: takes ward + category + growth_type, returns per-period table with formula shown.
    input: target ward (string), category (string), and growth_type (string, e.g., MoM or YoY).
    output: A per-period table of results explicitly showing the calculated growth and the formula used (table).
    error_handling: If growth_type is not specified, or if asked to aggregate across wards/categories, refuse and ask.
