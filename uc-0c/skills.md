skills:
  - name: load_dataset
    description: >
      Reads the ward budget CSV, validates required columns, and reports null
      actual_spend count and which rows before returning data.
    input: >
      File path to ward_budget.csv (period, ward, category, budgeted_amount,
      actual_spend, notes).
    output: >
      Validated row list plus a null report: count of null actual_spend rows,
      and for each null row the period, ward, category, and notes reason.
    error_handling: >
      If the file is missing, unreadable, empty, or missing required columns,
      raise a clear error and refuse to compute. Never invent rows or fill
      null spends. Always surface the null report before any growth calculation.

  - name: compute_growth
    description: >
      Takes ward + category + growth_type and returns a per-period table with
      the formula shown on every row; null periods are flagged not computed.
    input: >
      Loaded dataset, ward string, category string, and growth_type (must be
      explicitly provided, e.g. MoM).
    output: >
      Per-period CSV rows for that ward+category only: period, ward, category,
      actual_spend, growth_pct (or NULL/FLAGGED), formula, flag/notes.
    error_handling: >
      Refuse all-ward or multi-category aggregation. Refuse if growth_type is
      missing or unsupported. If ward/category has no rows, refuse. For null
      current or previous actual_spend, flag the row with notes reason and skip
      the numeric growth (no silent skip, no imputation).
