# skills.md — UC-0C Growth Calculator

skills:
  - name: load_dataset
    description: >
      Read the ward-budget CSV, validate required columns, and report null
      actual_spend count and row identities before returning the data.
    input: >
      input_path (string path to a CSV, e.g. ../data/budget/ward_budget.csv).
      Expected columns: period, ward, category, budgeted_amount, actual_spend,
      notes.
    output: >
      A structured object: validated rows (list of dicts preserving blanks as
      null), plus a null_report with null_count and a list of null rows each
      identifying period, ward, category, and notes reason. Callers must see
      the null report before any growth computation.
    error_handling: >
      If the file is missing, unreadable, or empty, raise a clear error and do
      not invent rows. If required columns are missing or misnamed, raise an
      error listing the expected schema. Never silently drop null rows or fill
      actual_spend — every blank actual_spend must appear in null_report with
      its notes reason.

  - name: compute_growth
    description: >
      Compute per-period growth for one ward and one category using an
      explicit growth_type, returning a table with formula shown on every row.
    input: >
      Loaded dataset from load_dataset, plus ward (exact string), category
      (exact string), growth_type (required string, e.g. MoM), and output_path
      for the results CSV.
    output: >
      A per-period CSV at output_path for the filtered ward × category only.
      Each row includes period, ward, category, actual_spend (or null),
      growth result (or null/flagged), formula used, and — when actual_spend
      is null — the notes reason. Not a single aggregated number.
    error_handling: >
      If growth_type is missing or unspecified, refuse and ask — never guess
      MoM vs YoY. If the request implies all-ward or cross-category
      aggregation, refuse. For null actual_spend periods (or a null previous
      period needed by the formula), flag the row with the notes reason and
      do not compute growth. If ward or category matches no rows, raise a
      clear error rather than widening the filter. Always write the formula
      string on every output row alongside the result or flag.
