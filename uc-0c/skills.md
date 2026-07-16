skills:
  - name: load_dataset
    description: Reads the budget CSV, validates required columns, reports null actual_spend rows before returning.
    input: "csv_path (str, path to ward_budget.csv)"
    output: "tuple (rows: list[dict], null_report: list[dict] with period/ward/category/notes for each null actual_spend row)"
    error_handling: >
      If a required column (period, ward, category, budgeted_amount, actual_spend) is missing
      from the header, raise a clear error naming the missing column rather than proceeding
      with a partial row shape.

  - name: compute_growth
    description: Takes ward, category, and growth_type, returns a per-period table with the formula shown for each row.
    input: "rows (list[dict] from load_dataset), ward (str), category (str), growth_type ('MoM' or 'YoY')"
    output: "list of dicts: [{period, actual_spend, formula, growth_pct}], one per period for that ward+category, in period order"
    error_handling: >
      If growth_type is missing or not one of MoM/YoY, raise an error asking the caller to
      specify one explicitly — never default to MoM silently. If actual_spend for a period is
      null, that period's row has growth_pct set to null and formula set to the null reason
      instead of a computed value, and it is excluded from the previous-period baseline of
      the next row's calculation.
