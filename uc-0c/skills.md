# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: load_dataset
    description: Reads the ward_budget CSV, validates the 6 expected columns (period, ward, category, budgeted_amount, actual_spend, notes), reports null count and which specific rows are null before returning data.
    input: A file path string pointing to a CSV with columns period, ward, category, budgeted_amount, actual_spend, notes.
    output: A dict with keys "columns" (list of validated column names), "rows" (list of dicts), "null_rows" (list of (row_index, period, ward, category, reason) for rows where actual_spend is null).
    error_handling: If the file is missing or unreadable, raise FileNotFoundError. If any of the 6 expected columns is missing, raise ValueError listing the missing columns. If the CSV is empty, raise ValueError("CSV is empty").

  - name: compute_growth
    description: Takes ward, category, and growth_type (MoM or YoY), filters matching rows sorted by period, flags null rows, and returns a per-period table with the growth formula and computed value for each row.
    input: ward (string), category (string), growth_type (string, must be "MoM" or "YoY"), dataset (dict from load_dataset).
    output: A list of dicts where each entry has period, actual_spend, previous_spend, formula_string, growth_value, plus a "notes_flag" for rows where actual_spend was null.
    error_handling: If growth_type is not "MoM" or "YoY", raise ValueError("growth_type must be 'MoM' or 'YoY'"). If ward or category not found in dataset, raise ValueError listing available wards/categories. If fewer than 2 periods exist for the given growth_type window, raise ValueError("Need at least 2 periods to compute growth").
