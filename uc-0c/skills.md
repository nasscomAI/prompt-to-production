# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: >
      Reads the ward budget CSV, validates that all required columns are present,
      identifies and reports every null actual_spend row (with period, ward,
      category, and notes reason) before returning the dataset for computation.
    input: >
      A file path string pointing to ward_budget.csv. Expected columns:
      period (YYYY-MM), ward (string), category (string),
      budgeted_amount (float), actual_spend (float or blank), notes (string).
    output: >
      A dict with:
        - data: list of row dicts (all rows, including null rows, unmodified)
        - null_rows: list of dicts for each row where actual_spend is blank/null,
          each containing: period, ward, category, null_reason (copied verbatim
          from notes column)
        - null_count: integer count of null actual_spend rows
        - columns_validated: bool — True if all required columns present
      Null rows are reported in this output before any growth computation begins
      (agents.md enforcement rule 2). They remain in `data` but are flagged
      in `null_rows` so compute_growth can skip them.
    error_handling: >
      If file_path does not exist: raise FileNotFoundError with a descriptive
      message — do not return partial output.
      If any required column is missing: raise ValueError listing the missing
      column names — do not attempt computation on an incomplete dataset.
      If actual_spend is missing from all rows: raise ValueError
      "No actual_spend values found — dataset may be malformed."

  - name: compute_growth
    description: >
      Takes a loaded dataset, a specific ward, a specific category, and an
      explicit growth type (MoM or YoY), and returns a per-period growth table
      where every row includes the formula used alongside the computed result.
    input: >
      Four arguments:
        - dataset: the dict returned by load_dataset (data + null_rows)
        - ward: exact ward name string (e.g. "Ward 1 – Kasba")
        - category: exact category string (e.g. "Roads & Pothole Repair")
        - growth_type: string — must be exactly "MoM" or "YoY"
      All four arguments are required. growth_type must be provided by the
      caller — this skill never defaults to either option (agents.md rule 4).
    output: >
      A list of dicts, one per period in source order, each containing:
        - period: YYYY-MM string
        - actual_spend: float or null
        - growth_pct: float (rounded to 1 dp) or null if row is flagged
        - formula: human-readable string showing the exact calculation, e.g.
            MoM: "((19.7 - 14.8) / 14.8) × 100 = +33.1%"
            YoY: "((19.7 - 18.2) / 18.2) × 100 = +8.2%"
        - flag: "NULL — <null_reason verbatim from notes>" if actual_spend is
          null, else blank string
      Rows where actual_spend is null have growth_pct: null, formula: null,
      and a populated flag — growth is never computed for null rows
      (agents.md enforcement rule 2). Formula is shown for every non-null row
      (agents.md enforcement rule 3).
    error_handling: >
      If growth_type is not "MoM" or "YoY": raise ValueError with the message:
      "Growth type not specified — please provide --growth-type MoM or
      --growth-type YoY." Do not default to either (agents.md enforcement rule 4).
      If ward or category produces no matching rows after filtering: raise
      ValueError "No rows found for ward='<ward>' category='<category>' —
      check exact spelling."
      If the request omits ward or category (i.e. would aggregate across all
      wards or all categories): raise ValueError with the refusal message:
      "Aggregation across wards/categories not permitted without explicit
      instruction — please specify a ward and category."
      (agents.md enforcement rule 1).
      If there is no prior period to compare against (e.g. first row for MoM):
      set growth_pct to null and formula to "No prior period — growth cannot
      be computed."
