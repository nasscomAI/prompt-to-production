# skills.md

skills:
  - name: load_dataset
    description: >
      Reads the ward budget CSV, validates its columns, and reports every null
      actual_spend row before returning the dataset.
    input: >
      Path to CSV (default ../data/budget/ward_budget.csv). Expected columns:
      period (YYYY-MM), ward, category, budgeted_amount, actual_spend (float
      or blank), notes.
    output: >
      A dataset object (rows filtered or full) plus a null-report listing each
      null actual_spend row: period, ward, category, and the reason quoted
      from the notes column.
    error_handling: >
      Refuses if any expected column is missing or the file cannot be read —
      reports the exact problem, never fabricates data.

  - name: compute_growth
    description: >
      Computes a per-period growth table for one ward + one category using the
      given growth type, with every null row flagged and the formula shown on
      every row.
    input: >
      Dataset from load_dataset, ward (string), category (string),
      growth_type (MoM or YoY), optional output path.
    output: >
      Per-period table (period, actual_spend, growth) for the requested
      ward/category. Null actual_spend rows are flagged with their notes
      reason and growth is NOT computed for them. Every row shows the formula
      used (e.g. MoM = (current−prev)/prev).
    error_handling: >
      Refuses if growth_type is missing or not MoM/YoY (asks instead of
      guessing), or if the ward/category does not exist in the dataset.
