skills:
  - name: load_dataset
    description: Reads and validates the ward budget CSV, identifies null rows, and reports them before returning the dataset.
    input: filepath (string, e.g., "../data/budget/ward_budget.csv")
    output: Dictionary with keys {data: DataFrame, null_rows: List[Dict], columns_found: List[str], row_count: int}. null_rows contains [period, ward, category, reason_from_notes] for all 5 null actual_spend rows.
    error_handling: Refuse if file not found, if required columns (period, ward, category, budgeted_amount, actual_spend, notes) are missing, or if CSV is malformed. Report exact column names and counts before proceeding.

  - name: compute_growth
    description: Calculates month-over-month or year-over-year growth for a specific ward and category, showing formula for every period.
    input: {dataset: DataFrame, ward: string, category: string, growth_type: string (MoM or YoY)}
    output: CSV string with columns [period, actual_spend, previous_period_spend, growth_percentage, formula_used]. Each row shows the arithmetic formula (e.g., "(19.7 - 14.8) / 14.8 * 100"). Null rows appear with actual_spend = NULL and formula_used = "Null — [reason from notes]".
    error_handling: Refuse if ward not found in dataset (report available wards). Refuse if category not found (report available categories). Refuse if growth_type is not "MoM" or "YoY". Refuse if the requested ward-category pair has no non-null rows. Do not compute or guess.
