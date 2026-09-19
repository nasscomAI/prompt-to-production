skills:
  - name: load_dataset
    description: Reads the budget CSV, validates columns, and reports the null actual_spend rows before returning the data.
    input: path (str) to a CSV with period, ward, category, budgeted_amount, actual_spend, notes.
    output: List of row dicts; prints the null count and each null row with its notes reason.
    error_handling: Unreadable file or missing required columns stops with a clear error message.

  - name: compute_growth
    description: Computes MoM or YoY growth for one ward and one category and returns a per-period table with the formula on every row.
    input: rows, ward (str), category (str), growth_type (MoM or YoY).
    output: List of rows with period, actual_spend, growth, formula, flag.
    error_handling: Unknown, ambiguous or "all" ward or category is refused. Null current or previous value gives an empty growth and a flag with the reason. A missing prior period (Jan for MoM, all months for YoY on 2024-only data) is flagged, not computed.