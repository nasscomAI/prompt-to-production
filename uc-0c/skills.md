skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates required columns, reports null count and which rows are null before returning the data.
    input: file_path (str) — path to ward_budget.csv.
    output: A tuple of (list of row dicts, list of null-row dicts with period/ward/category/notes); raises on missing columns.
    error_handling: Raises FileNotFoundError if path missing; raises ValueError if required columns (period, ward, category, budgeted_amount, actual_spend, notes) are absent; prints null row report to stderr before returning.

  - name: compute_growth
    description: Takes a filtered list of rows for one ward and one category, computes per-period growth using the specified growth type, and returns a table with formula shown per row.
    input: rows (list of dicts filtered to one ward+category), growth_type (str, must be "MoM" or "YoY").
    output: List of dicts with keys period, actual_spend, growth_pct, formula, flag; null rows included with growth_pct=NULL and flag=FLAGGED.
    error_handling: Raises ValueError if growth_type is not MoM or YoY; sets growth_pct to NULL and flag to FLAGGED for null actual_spend rows; sets growth_pct to NULL and flag to NO_PRIOR_PERIOD for the first row where no previous value exists.
