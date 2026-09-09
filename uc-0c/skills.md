skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates required columns exist, and reports which rows have null actual_spend before any computation happens.
    input: A file path (string) to a CSV with columns period, ward, category, budgeted_amount, actual_spend, notes.
    output: A validated table (DataFrame) plus a printed list of null rows with their period, ward, category, and null reason from notes.
    error_handling: If required columns are missing, raise an error naming which columns are absent. If actual_spend is null, the row is flagged with its notes reason — never silently dropped or treated as zero.

  - name: compute_growth
    description: Computes MoM or YoY growth for one specified ward and category, returning a per-period table with the formula shown for each row.
    input: The validated table, a ward (string), a category (string), and a growth_type (string, must be "MoM" or "YoY").
    output: A per-period list of rows containing period, actual_spend, growth_pct, formula, and a flag field for anything not computed.
    error_handling: If ward or category is missing (i.e. an aggregate request), refuse with an explicit message. If growth_type is missing or invalid, refuse and ask rather than defaulting. If actual_spend or the required prior period is null, mark the row as flagged with growth_pct as None instead of computing a number.