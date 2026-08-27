# skills.md

skills:
  - name: load_dataset
    description: >
      Read a municipal budget CSV, validate its schema and values, and audit all
      missing actual-spend rows before any calculation.
    input: >
      A readable CSV path. Required columns are period, ward, category,
      budgeted_amount, actual_spend, and notes; period must use YYYY-MM and
      numeric fields must be valid numbers when present.
    output: >
      A period-sorted list of validated row records, plus a null audit containing
      the count and the period, ward, category, and notes for every blank
      actual_spend.
    error_handling: >
      Refuse with a clear error for unreadable/empty files, missing columns,
      invalid periods, duplicate ward-category-period rows, invalid numeric
      values, or blank null reasons.

  - name: compute_growth
    description: >
      Calculate period-by-period actual-spend growth for exactly one explicit
      ward-category pair using an explicit MoM or YoY comparison.
    input: >
      Validated dataset records, one exact ward string, one exact category
      string, and growth_type equal to MoM or YoY (case-insensitive).
    output: >
      A per-period table with ward, category, actual_spend, comparison period and
      value, growth_type, growth_percent, formula, status, and null_reason.
    error_handling: >
      Refuse wildcard, all-level, missing, unknown, or ambiguous selections;
      refuse missing/unsupported growth types and zero denominators. For absent
      comparison periods or null operands, emit a flagged row with blank growth
      instead of guessing, filling, dropping, or treating null as zero.
