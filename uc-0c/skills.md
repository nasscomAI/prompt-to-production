# UC-0C — Number That Looks Right
# skills.md — skills for the growth-analysis agent

skills:
  - name: load_dataset
    description: >
      Reads and validates ../data/budget/ward_budget.csv, reports row count,
      NULL actual_spend count, and every NULL row with its notes reason, then
      returns the validated dataset.
    input: Path to the budget CSV (../data/budget/ward_budget.csv).
    output: >
      Validated dataset with all NULL actual_spend preserved (never converted
      to zero). Additionally reports: total row count; count of NULL/blank
      actual_spend values; a list of every NULL row with period, ward,
      category, and the reason from the notes column.
    error_handling:
      - >
        Missing file → raise a clear error stating the expected path and that
        the dataset is required; do not proceed.
      - >
        Missing/invalid columns → raise a clear error listing the required
        columns (period, ward, category, budgeted_amount, actual_spend,
        notes) and which are missing; do not proceed.
      - >
        NULL actual_spend → never convert to zero or invent a value; flag
        each row with its notes reason.

  - name: compute_growth
    description: >
      Computes a per-period growth table for an explicitly requested ward +
      category + growth_type, showing the formula in every row and flagging
      NULL-driven rows.
    input: ward (string), category (string), growth_type (MoM or YoY).
    output: >
      Per-period table (not a single aggregated number) for exactly the
      requested ward and category, preserving period, actual_spend, growth,
      formula, and null/flag info. For MoM per row:
      ((current actual_spend − previous actual_spend) / previous actual_spend)
      × 100.
    error_handling:
      - >
        Missing/unsupported growth_type → REFUSE; ask the user to specify
        MoM or YoY. Never guess.
      - >
        Invalid ward or category (not present in the data) → raise a clear
        error; do not substitute another ward or category.
      - >
        NULL current or previous actual_spend → do not compute that growth
        value; flag the row with the NULL reason from notes.
      - >
        All-ward or cross-category aggregation request → REFUSE; compute only
        the requested ward + category. Cross-ward or cross-category
        calculation is not computed.