skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates required columns, and reports NULL actual_spend rows (with reasons) before returning data.
    input: >
      path: string (CSV file path). Expected columns: period (YYYY-MM), ward, category,
      budgeted_amount, actual_spend, notes.
    output: >
      data: table/rows; plus a validation report including row count, distinct ward/category counts,
      NULL actual_spend count, and the list of NULL rows with (period, ward, category, notes).
    error_handling: >
      If the file is missing/unreadable, required columns are absent, period format is invalid,
      or types cannot be parsed, stop and return a clear error describing what failed and what
      the expected schema is.

  - name: compute_growth
    description: Computes growth for one ward and one category as a per-period table, showing the formula used and flagging periods that cannot be computed.
    input: >
      data: output of load_dataset; ward: string; category: string; growth_type: enum {MoM, YoY}.
    output: >
      A per-period table for the requested ward+category with columns:
      period, ward, category, actual_spend, growth_type, growth_value, formula, flags.
      For periods with NULL actual_spend (or missing prior period needed for growth), growth_value
      must be blank/NULL and flags must explain why.
    error_handling: >
      If ward/category do not exist in the dataset, if growth_type is missing/unknown, or if an
      all-ward/all-category aggregate is requested, refuse with a specific message describing the
      accepted inputs and required parameters.
