skills:
  - name: load_dataset
    description: Reads the ward_budget CSV, validates required columns are present, and reports the total null count and which specific rows have null actual_spend values (with their period, ward, category, and notes reason) before returning the full dataset.
    input: A file path string pointing to the ward_budget CSV file.
    output: A dict containing two keys — "rows" (list of all row dicts from the CSV) and "nulls" (list of dicts for each null actual_spend row, each with keys period, ward, category, budgeted_amount, and null_reason from the notes column).
    error_handling: If the file is not found, raise FileNotFoundError with the path. If required columns (period, ward, category, budgeted_amount, actual_spend, notes) are missing, raise ValueError listing missing columns. If the file is empty, raise ValueError. Never silently swallow errors or return partial data.

  - name: compute_growth
    description: Takes a ward, category, growth type (MoM or YoY), and the dataset returned by load_dataset, filters to the specified ward and category, and returns a per-period growth table with the formula and input values shown for every computed row and NULL_FLAGGED shown for every null row.
    input: A dict with keys ward (string), category (string), growth_type (string — must be exactly "MoM" or "YoY"), and dataset (the dict returned by load_dataset).
    output: A list of dicts, one per period, each containing period, actual_spend (or "NULL"), growth_pct (float rounded to 1 decimal place, or "NULL_FLAGGED"), formula_shown (string showing the formula with substituted values, e.g. "(19.7 - 14.8) / 14.8 * 100" for MoM), and null_reason (string or blank).
    error_handling: If growth_type is not "MoM" or "YoY", raise ValueError and prompt the caller to specify explicitly — never default. If the ward or category is not found in the dataset, raise ValueError listing available values. If a null row is involved in a growth calculation (either as current or previous period), mark the growth for that period as NULL_FLAGGED and record the null_reason — never compute across a null.
