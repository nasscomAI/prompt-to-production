# skills.md

skills:
  - name: load_dataset
    description: Read the ward budget CSV and validate structure plus null inventory.
    input: >
      `input_path` to `../data/budget/ward_budget.csv` containing columns: `period`, `ward`,
      `category`, `budgeted_amount`, `actual_spend`, `notes`.
    output: >
      A structured dataset object with parsed rows, schema validation result, and a null report that
      includes null count and row identifiers (period, ward, category) with `notes` reason for each
      null `actual_spend`.
    error_handling: >
      If required columns are missing, period format is invalid, or numeric parsing fails, return a
      validation error and stop computation. Never auto-correct schema or silently coerce malformed
      fields.

  - name: compute_growth
    description: Compute period-wise growth for one ward and one category using explicit growth type.
    input: >
      Structured dataset from `load_dataset`, `ward`, `category`, and `growth_type` (required; e.g.,
      MoM or YoY).
    output: >
      A per-period table (not aggregated across wards/categories) including:
      `period`, `ward`, `category`, `actual_spend`, `growth_type`, `formula`, `growth_value`,
      `status` (COMPUTED or NOT_COMPUTED), and `null_reason` where applicable.
      Rows with null-required operands must be flagged and not numerically computed.
    error_handling: >
      Refuse when growth type is missing/unsupported, ward/category is ambiguous, or request implies
      all-ward/all-category aggregation without explicit authorization. For null rows, emit
      NOT_COMPUTED with the source `notes` reason instead of fabricating values.
