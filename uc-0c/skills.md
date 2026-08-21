# skills.md — UC-0C Ward Budget Growth Analyzer

skills:
  - name: load_dataset
    description: Reads the budget CSV, validates its columns, and reports the null count and which rows are null before returning.
    input: path (string) to ward_budget.csv with columns period, ward, category, budgeted_amount, actual_spend, notes.
    output: List of row dicts plus the distinct ward and category lists; prints a pre-flight report of every null actual_spend row with its notes reason.
    error_handling: Missing required columns, missing file, or non-UTF-8 encoding exits with a clear stderr message and exit code 1; malformed rows are skipped with a warning instead of crashing.

  - name: compute_growth
    description: Takes a ward + category + growth type and returns the per-period growth table with the formula shown on every computed row.
    input: rows (from load_dataset), ward (exact ward name), category (exact category name), growth_type ("MoM" or "YoY").
    output: One output row per period sorted by period, containing period, spend, previous spend, growth percentage, formula string, and flag; null periods are flagged NULL_SPEND with the notes reason and never computed.
    error_handling: Ward or category not present in the dataset is reported with the list of valid values (exit 1); growth is not computed across a null gap — the following period is flagged NOT COMPUTED; division by a zero base is flagged rather than raising.
