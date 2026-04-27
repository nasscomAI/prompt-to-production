
skills:
  - name: load_dataset
    description: >
      Loads the budget CSV dataset and validates its structure before any
      computation is performed.
    input: >
      Path to a CSV file containing ward-level budget data.
    output: >
      A validated dataset with confirmed columns and an explicit report of:
      - Total row count
      - Rows with null actual_spend values (including ward, category, period, and notes)
    error_handling: >
      If required columns are missing, the file is unreadable, or the dataset
      shape does not match expectations, the skill must fail explicitly.
      Null values must never be silently ignored or filled.

  - name: compute_growth
    description: >
      Computes growth values (MoM or YoY) for a single ward and single category,
      period by period, using actual_spend values only.
    input: >
      - Validated dataset  
      - ward (string, required)  
      - category (string, required)  
      - growth_type (explicitly specified: MoM or YoY)
    output: >
      A per-period table for the specified ward and category showing:
      - period
      - actual_spend
      - growth value
      - growth formula used
    error_handling: >
      If growth_type is missing or ambiguous, the skill must refuse to run.
      If any required period contains a null actual_spend value, that period
      must be flagged and excluded from growth computation rather than computed.

  - name: validate_output
    description: >
      Validates that the computed output complies with all UC‑0C constraints.
    input: >
      Source dataset parameters and the generated growth table.
    output: >
      Pass/fail validation result with explicit reasons for failure, if any.
    error_handling: >
      The skill must fail if:
      - Output aggregates across multiple wards or categories
      - A single aggregated growth number is returned
      - Null rows are not explicitly flagged
      - Growth formulas are missing from output
