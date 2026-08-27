# skills.md

skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates required columns, and reports the null actual_spend rows by ward/category/period with their notes reasons before returning.
    input: Path to the CSV file (string).
    output: Structured dataset with all non-null rows plus a list of every null actual_spend row (period, ward, category, notes reason) and the null count.
    error_handling: If the file is missing, unreadable, or missing required columns (period, ward, category, budgeted_amount, actual_spend, notes), raise/return an explicit error.

  - name: compute_growth
    description: Computes period-over-period growth for a single requested ward and category using the specified growth type, returning a per-period table with the formula shown and null rows flagged.
    input: The loaded dataset, a ward name (string), a category name (string), and a growth type (string, e.g. MoM).
    output: Ordered per-period rows for that ward/category, each with actual_spend, computed growth %, and the formula used; null actual_spend rows flagged with their notes reason and no computed growth value.
    error_handling: If the growth type is missing or unsupported (e.g. YoY with no prior-year data), or the ward/category has no data, report and refuse rather than guess.
