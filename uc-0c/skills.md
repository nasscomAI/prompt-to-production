skills:
  - name: load_dataset
    description: >
      Read the budget CSV, validate its required schema, and report missing
      actual_spend rows before returning data for analysis.
    input: >
      A CSV file path. The file must contain period, ward, category,
      budgeted_amount, actual_spend, and notes columns.
    output: >
      A validated dataset plus a null report containing the total null count
      and, for every null actual_spend row, its period, ward, category, and
      reason from notes.
    error_handling: >
      Refuse and report the validation error if the file is unreadable, required
      columns are missing, or values cannot be parsed. Do not drop, fill, or
      silently ignore null actual_spend rows.

  - name: compute_growth
    description: >
      Compute growth by period for exactly one requested ward and category,
      preserving a formula alongside each computable result.
    input: >
      A validated dataset, one explicit ward, one explicit category, and an
      explicit growth_type such as MoM or YoY.
    output: >
      A per-period table for only the requested ward/category, including the
      values used, the growth result where computable, and the formula used in
      each output row. Rows with null actual_spend are flagged and not computed.
    error_handling: >
      Refuse if ward, category, or growth_type is missing or ambiguous; never
      guess the growth method. Refuse all-ward or all-category aggregation.
      Before calculation, report every applicable null row and its notes reason.
