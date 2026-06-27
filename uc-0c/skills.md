# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: Reads the CSV, validates columns, and reports null count and exact rows with nulls before returning data.
    input: file_path (str) - The path to the CSV dataset.
    output: data (list of dicts) - The parsed CSV data.
    error_handling: Raise an error if the file is missing or malformed.

  - name: compute_growth
    description: Takes the dataset, filters by ward and category, and computes the requested growth type, returning a per-period table with the formula shown.
    input: data (list of dicts), ward (str), category (str), growth_type (str)
    output: result_table (list of dicts) - The calculated growth table with explicit null flagging.
    error_handling: Refuse to compute if growth_type is missing or invalid. Refuse to aggregate across multiple wards/categories.
