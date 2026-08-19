# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: Reads the ward_budget.csv, validates required columns, reports the total null count and which specific rows have null actual_spend before returning the filtered dataset for a given ward and category.
    input: >
      - file_path (string): path to ward_budget.csv.
      - ward (string): exact ward name to filter on (e.g. "Ward 1 – Kasba").
      - category (string): exact category name to filter on (e.g. "Roads & Pothole Repair").
    output: >
      A dict with two keys:
        - rows (list of dicts): filtered rows for the given ward+category, each containing
          period (string YYYY-MM), ward, category, budgeted_amount (float), actual_spend
          (float or None), notes (string).
        - null_report (list of dicts): one entry per null actual_spend row, each containing
          period, ward, category, and notes — reported BEFORE any computation begins.
      Prints to stdout: "Loaded N rows for [ward] / [category]. Nulls found: M — [period list]."
    error_handling: >
      If file_path does not exist — print error and exit with code 1.
      If any required column (period, ward, category, actual_spend, notes) is missing — print
      the missing column name and exit with code 1.
      If no rows match the given ward+category combination — print
      "No data found for [ward] / [category]. Check exact names." and exit with code 1.
      If ward or category argument is blank or not provided — refuse and print
      "Ward and category must both be specified — cannot operate on full dataset."

  - name: compute_growth
    description: Takes the filtered rows from load_dataset and computes per-period MoM or YoY growth, showing the formula used for every row and flagging null periods instead of computing them.
    input: >
      - rows (list of dicts): filtered dataset from load_dataset (ward+category already applied).
      - null_report (list of dicts): null rows from load_dataset — these periods must be flagged, not computed.
      - growth_type (string): must be explicitly "MoM" or "YoY" — no default, no inference.
    output: >
      A list of result dicts, one per period, each containing:
        - period (string YYYY-MM)
        - actual_spend (float or "NULL")
        - growth_value (float or "NULL — not computed")
        - formula (string): e.g. "MoM: (19.7 - 14.8) / 14.8 × 100 = +33.1%" or "NULL — skipped"
        - flag (string): "NULL_SPEND — see notes: [notes text]" for null rows, else blank
      The result list is also written to growth_output.csv via the caller.
    error_handling: >
      If growth_type is not "MoM" or "YoY" — raise ValueError:
      "growth_type must be MoM or YoY — never inferred. Please specify explicitly."
      If rows list is empty — raise ValueError: "No rows to compute — check load_dataset output."
      If a null row is encountered during computation — flag it with NULL_SPEND and the notes
      value; never zero-fill, interpolate, or skip silently.
