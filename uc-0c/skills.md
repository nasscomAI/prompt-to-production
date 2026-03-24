skills:
  - name: load_dataset
    description: Reads the budget CSV, validates columns, and reports the count and locations of null actual_spend rows before returning the data.
    input: file_path (str)
    output: A dict containing 'rows' (list of dicts) and 'null_report' (list of dicts with null details).
    error_handling: Raise an exception if required columns are missing or file is not found.

  - name: compute_growth
    description: Takes a filtered dataset for a specific ward and category, and computes the specified growth_type (MoM or YoY). Returns a table including the formula used, ignoring non-computable rows but preserving their flags.
    input: data_rows (list of dicts), ward (str), category (str), growth_type (str)
    output: A list of result dicts containing period, actual_spend, formula, growth_pct, and null_flag.
    error_handling: Refuse and return an error message if ward or category are not specific, or if growth_type is missing/invalid.
