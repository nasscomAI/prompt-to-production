skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates its columns, and reports null actual_spend rows before any computation happens.
    input: "Path to ward_budget.csv with columns: period, ward, category, budgeted_amount, actual_spend, notes."
    output: "Parsed rows as a list of dicts, plus a separate list of flagged null rows (period, ward, category, notes reason)."
    error_handling: >
      If the file is missing or unreadable, raise a clear error and stop.
      If expected columns are missing, raise an error naming which columns
      are absent rather than proceeding with partial data. Null actual_spend
      rows are not treated as errors — they are collected and reported, not
      skipped silently.

  - name: compute_growth
    description: Computes MoM or YoY growth for one ward and one category across all available periods, showing the formula used.
    input: "ward (string), category (string), growth_type (MoM or YoY), and the loaded dataset rows."
    output: "A per-period table with period, actual_spend, growth_percent, formula_used, and a null flag/reason where applicable."
    error_handling: >
      Refuses and returns an error if growth_type is missing or not one of
      MoM/YoY. Refuses if ward or category is not found in the dataset, or if
      more than one ward/category would be aggregated together. For periods
      where either the current or comparison period has a null actual_spend,
      growth is not computed — the row is marked as flagged with the reason
      instead of a numeric value.