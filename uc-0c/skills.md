# skills.md

skills:
  - name: load_dataset
    description: Reads ward_budget.csv, validates all required columns, counts and lists null rows before returning data.
    input: CSV file path (string). Expected columns — period (YYYY-MM), ward, category, budgeted_amount, actual_spend, notes.
    output: Dict with keys {data: DataFrame, null_count: int, null_rows: list of {date, ward, category, reason}}. Null rows sorted by date.
    error_handling: REFUSE if file not found. REFUSE if required columns missing. Report null_count and null_row_details to user before proceeding to computation.

  - name: compute_growth
    description: Computes MoM or YoY growth for a specific ward and category, returning per-period table with formula shown.
    input: Dict with keys {ward: str, category: str, growth_type: 'MoM'|'YoY', data: DataFrame}.
    output: DataFrame with columns {period, actual_spend, growth_rate, formula}. Rows ordered by date. Growth rate as ±XX.X%. Formula as '(new - old) / old = ±XX.X%'.
    error_handling: REFUSE if ward or category not found in data. REFUSE if growth_type not 'MoM' or 'YoY'. For null actual_spend cells, mark formula as 'NULL — see reason' and repeat reason from notes column. Never skip or impute nulls.
