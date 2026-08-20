skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates required columns, identifies and reports every null actual_spend row (with its note reason) before returning the data.
    input: File path (string) to the ward_budget.csv.
    output: Dict containing — rows (list of dicts, all 300 rows), null_rows (list of dicts for the 5 null rows, each including period/ward/category/notes), column validation status.
    error_handling: If the file is missing or unreadable, halt with an error. If required columns (period, ward, category, budgeted_amount, actual_spend, notes) are absent, halt and name the missing columns. Always report null count and which rows before returning — never silently skip them.

  - name: compute_growth
    description: Takes a specific ward, category, and growth type (MoM only), filters the dataset to that slice, and returns a per-period table showing actual_spend, the previous period value, the computed growth percentage, and the exact formula used for every row.
    input: rows (list of dicts from load_dataset), ward (str), category (str), growth_type (str — must be "MoM"; refuse if anything else or if not provided).
    output: List of dicts per period with columns — period, ward, category, actual_spend, previous_spend, growth_pct, formula, flag, note. Null rows are flagged with flag=NULL_FLAGGED and growth_pct left blank; formula is shown even when growth cannot be computed.
    error_handling: If ward or category is not found in the dataset, return an error naming the valid options. If growth_type is not "MoM", refuse and state the allowed values. If the previous period is null, flag the current row as NULL_DEPENDENCY and do not compute growth. Never aggregate across wards or categories — if called without a specific ward and category, refuse.
