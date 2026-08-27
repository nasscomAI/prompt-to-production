skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates required columns, and reports null counts and specific null rows before returning the data.
    input: File path to the CSV file (string).
    output: A list of dictionaries representing the CSV rows, plus a summary report of nulls.
    error_handling: If the file is missing or columns are invalid, raise an error. For failure modes like silent null handling, ensure all null rows are identified and reported with reasons from notes. If nulls are present, do not proceed without flagging.

  - name: compute_growth
    description: Computes growth rates for a specific ward and category using the specified growth type, producing a per-period table.
    input: Ward name (string), category name (string), growth type (string, e.g., 'MoM'), and the loaded dataset (list of dicts).
    output: A list of dicts with period, actual_spend, growth_percentage, formula_used, null_flag.
    error_handling: If ward or category not found, or growth_type invalid, return error. For wrong aggregation, refuse if multiple wards/categories implied. For formula assumption, require explicit growth_type. Flag nulls and skip growth calculation for them.
