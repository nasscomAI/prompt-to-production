skills:
  - name: load_dataset
    description: Reads a ward budget CSV, validates required columns (period, ward, category, budgeted_amount, actual_spend, notes), reports total rows, and lists every row with a null actual_spend along with the reason from the notes column.
    input: Path to a CSV file (string).
    output: Dict with keys "data" (list of dicts), "null_rows" (list of dicts with period, ward, category, reason), "row_count" (int).
    error_handling: Returns an error dict if the file does not exist, is not a CSV, or is missing required columns. Does not fall back or impute data.

  - name: compute_growth
    description: Takes filtered data for one ward and one category, sorted by period, and computes growth using the specified type (MoM or YoY). Returns a table with period, actual_spend, formula string, growth percentage (or N/A for first period), null flags, and null reasons.
    input: Dict with keys "ward" (string), "category" (string), "rows" (list of dicts sorted by period), "growth_type" ("MoM" or "YoY").
    output: List of dicts with keys "ward", "category", "period", "actual_spend", "growth_formula", "growth_pct", "null_flag", "null_reason".
    error_handling: Returns an error if growth_type is not "MoM" or "YoY". Returns empty growth_pct and "N/A" for the first period. Sets null_flag="YES" and includes the null reason for rows with missing actual_spend. Never imputes or estimates null values.
