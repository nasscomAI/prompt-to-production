# skills.md — UC-0C Budget Growth Analyser

skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates required columns are present, and reports the total null count and which specific rows have null actual_spend before returning the data.
    input: file_path (string path to ward_budget.csv).
    output: A dict with keys 'rows' (list of row dicts), 'null_count' (int), and 'null_rows' (list of dicts with period, ward, category, notes for each null row).
    error_handling: If the file does not exist, raise FileNotFoundError. If any required column (period, ward, category, budgeted_amount, actual_spend, notes) is missing, raise ValueError naming the missing column. Never silently ignore missing columns or null rows.

  - name: compute_growth
    description: Takes filtered rows for one ward and one category, computes the specified growth type per period, flags nulls, and returns a table with period, actual_spend, mom_growth or yoy_growth, formula, and null_flag columns.
    input: rows (list of row dicts for one ward+category, sorted by period), growth_type (string, either 'MoM' or 'YoY').
    output: A list of dicts, one per period, each with keys: period, actual_spend, growth_pct (string with % or 'N/A (no prior period)' or 'NULL_FLAGGED'), formula (string showing the arithmetic), null_flag (string 'NULL_FLAGGED' or blank), null_reason (string from notes column or blank).
    error_handling: If growth_type is not 'MoM' or 'YoY', raise ValueError and prompt the caller to specify one. If the filtered rows list is empty (ward/category not found), raise ValueError naming the missing combination.
