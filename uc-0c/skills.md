# skills.md

skills:
  - name: load_dataset
    description: >
      Reads the ward budget CSV, validates the required columns, reports
      how many actual_spend values are null and which (period, ward, category)
      rows they correspond to, then returns the parsed rows.
    input: >
      path (str) — filesystem path to a CSV with columns:
      period (YYYY-MM), ward (str), category (str), budgeted_amount (float),
      actual_spend (float or blank), notes (str).
    output: >
      A list of dict rows plus a null_report dict of the form
      {"null_count": int, "null_rows": [{"period","ward","category","notes"}, ...]}.
      The null_report is printed to stderr before the caller uses the rows.
    error_handling: >
      If the file is missing, unreadable, or missing any required column,
      raise a clear error and exit non-zero. Do not attempt to guess column
      names or coerce malformed rows.

  - name: compute_growth
    description: >
      Given the loaded rows, a ward, a category, and a growth_type
      (MoM or YoY), returns a per-period table for that single slice with
      actual_spend, growth_pct, and the formula string used for each row.
      Null actual_spend rows are flagged (growth_pct=NULL, reason from notes)
      and never computed.
    input: >
      rows (list[dict]) from load_dataset, ward (str exact match),
      category (str exact match), growth_type (Literal["MoM","YoY"]).
    output: >
      A list of dict rows, one per period in the slice, with fields:
      period, ward, category, actual_spend, growth_pct, formula, note.
    error_handling: >
      If ward or category has no matching rows, refuse and exit non-zero.
      If growth_type is missing or unsupported, refuse and ask the user
      to specify. If a required prior period is missing or null, emit
      growth_pct=NULL with reason 'prior period unavailable' — never impute.
