skills:
  - name: load_dataset
    description: Reads and validates the municipal budget CSV, then reports every null actual_spend row before returning data.
    input: "Path to a UTF-8 CSV containing period, ward, category, budgeted_amount, actual_spend and notes."
    output: "A validated list of typed budget rows; also prints a null report with count, row identity and notes reason."
    error_handling: "Stop with a clear error for an unreadable file, missing or invalid columns, malformed periods or numbers, duplicate ward-category-period rows, or a null actual_spend without a notes reason. Never impute a missing value."

  - name: compute_growth
    description: Filters to one ward and one category and computes an auditable per-period MoM or YoY growth table.
    input: "Validated budget rows plus one exact ward, one exact category and an explicit growth_type of MoM or YoY."
    output: "Chronological rows containing period, ward, category, current and comparison spend, growth type, displayed formula, growth percent, status and notes."
    error_handling: "Refuse all-scope, ambiguous or unknown selections and unsupported or missing growth types. Preserve rows but leave growth blank with an explicit status when the current/comparison value is null, history is unavailable or the comparison value is zero."
